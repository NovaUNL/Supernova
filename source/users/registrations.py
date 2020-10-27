import logging
import random
import string

from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

import college.models as college
import users.models as users
import settings
from supernova.utils import correlation
from users import triggers
from users.exceptions import InvalidToken, ExpiredRegistration, AccountExists
import jinja2

from users.utils import calculate_points, award_user


def validate_token(email, token) -> users.User:
    """
    | Perform validation of a confirmation email-token pair, completing the registration process.
    | Raises :py:class:`users.exceptions.InvalidToken` if the provided token is invalid.
    | Raises :py:class:`users.exceptions.ExpiredRegistration` if the allowed time span has passed, if the registration
        was already used or if there were too many attempts to finish the registration process.
    | Raises :py:class:`users.exceptions.AccountExists` if the email was already used to register
        another account or if the requested username was registered and validated by someone
        else during the validation time.

    :param email: Registration email
    :param token: Corresponding token
    :return: Created user
    """
    same_email_registrations = users.Registration.objects.filter(email=email).exclude(resulting_user=None)
    if same_email_registrations.exists():
        raise ExpiredRegistration('Já foi completado um registo neste email.')

    registration = users.Registration.objects.filter(email=email, token=token).first()
    if registration is None:
        raise ExpiredRegistration('Não foi possível encontrar um registo com este email.')

    if registration.token != token:  # Incorrect token
        if registration.failed_attempts < settings.REGISTRATIONS_ATTEMPTS_TOKEN - 1:
            registration.failed_attempts += 1
            registration.save(update_fields=['failed_attempts'])
            raise InvalidToken()
        else:
            raise InvalidToken(deleted=True)

    if registration.failed_attempts > settings.REGISTRATIONS_ATTEMPTS_TOKEN:
        raise ExpiredRegistration("Já tentou validar este registo demasiadas vezes.")

    elapsed_minutes = (timezone.now() - registration.creation).seconds / 60
    if elapsed_minutes > settings.REGISTRATIONS_TIMEWINDOW:
        raise ExpiredRegistration('O registo foi validado após o tempo permitido.')

    if users.User.objects.filter(email=registration.email).exists():
        raise AccountExists(f'Foi validada outra conta com o email {registration.email}.')

    if registration.requested_student:
        if registration.requested_student.user is not None:
            raise AccountExists(f"O estudante solicitado já foi associado a outra conta.")

        equivalent_students_registered = \
            college.Student.objects \
                .filter(abbreviation=registration.requested_student.abbreviation) \
                .exclude(user=None) \
                .exists()
        if equivalent_students_registered:
            logging.critical(f"Student {registration.requested_student.abbreviation} is partially associated.")
            raise AccountExists(f"O estudante solicitado já foi parcialmente associado a outra conta.")

    if registration.requested_teacher and registration.requested_teacher.user is not None:
        raise AccountExists(f"O professor solicitado já foi associado a outra conta.")

    if users.User.objects.filter(nickname=registration.nickname).exists():
        raise AccountExists("Desde que o registo foi feito registou-se outro utilizador com a alcunha "
                            f"'{registration.nickname}'. É necessário um novo registo.")

    if users.User.objects.filter(nickname=registration.username).exists():
        raise AccountExists("Desde que o registo foi feito registou-se outro utilizador com o username "
                            f"'{registration.username}'. É necessário um novo registo.")

    # Registration request accepted
    with transaction.atomic():
        user = users.User.objects.create_user(
            username=registration.username,
            email=registration.email,
            nickname=registration.nickname,
            last_activity=timezone.now(),
            password=registration.password,
        )
        user.save()
        registration.resulting_user = user
        registration.save(update_fields=['resulting_user'])

        try:
            if registration.requested_teacher:
                student_name = None
                if registration.requested_student:
                    student_name = registration.requested_student.name
                # Teacher email is known and matches or names are very very close
                if registration.email.split('@')[0] == registration.requested_teacher.abbreviation or \
                        (student_name and correlation(student_name, registration.requested_teacher.name) > 0.9):
                    triggers.teacher_assignment(user, registration.requested_teacher)
                else:
                    # Do nothing, those need to be approved manually
                    users.GenericNotification.objects.create(
                        receiver=user,
                        message='O professor reivindicado no seu registo não foi automáticamente associado. '
                                'Poderá vir a ser contactado/a.')

            if registration.requested_student:
                if registration.requested_student.abbreviation:
                    equivalent_student_filter = Q(abbreviation=registration.requested_student.abbreviation)
                else:
                    equivalent_student_filter = Q(id=registration.requested_student.id)

                owned_students = college.Student.objects.filter(equivalent_student_filter).all()
                for student in owned_students:
                    triggers.student_assignment(user, student)

                if len(owned_students) == 1 and owned_students[0].first_year == settings.COLLEGE_YEAR:
                    offset = users.ReputationOffset.objects.create(
                        amount=10,
                        receiver=user,
                        reason='Prémio para caloiros :)')
                    offset.issue_notification()

            user.calculate_missing_info()
            user.updated_cached()
            user_count = users.User.objects.count()
            if user_count < 100:
                offset = users.ReputationOffset.objects.create(
                    amount=1000,
                    receiver=user,
                    reason='Primeiros 100 utilizadores')
                offset.issue_notification()
            elif user_count < 1000:
                offset = users.ReputationOffset.objects.create(
                    amount=500,
                    receiver=user,
                    reason='Primeiros 1000 utilizadores')
                offset.issue_notification()
        except Exception as e:
            logging.error(f'Failed to take intermediate steps in {registration}.\n{str(e)}')
        finally:
            try:
                user.updated_cached()
                calculate_points(user)
                award_user(user)
            except Exception as e:
                logging.error(f'Failed to finalize the registration {registration}.\n{str(e)}')
            return user


def generate_token(length: int) -> str:
    """
    Generates a random alphanumeric mixed-case token.
    :param length: Token length
    :return: Token
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def email_confirmation(request, registration: users.Registration):
    """
    Sends a registration validation email.
    :param request: Request that originated this call
    :param registration: :py:class:`users.models.Registration` for which the email is sent after.
    """
    link = f"https://{request.get_host()}{reverse('registration_validation')}?email={registration.email}&token={registration.token}"
    manual_link = f"https://{request.get_host()}{reverse('registration_validation')}"
    token = registration.token
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('users/templates/users'),
        autoescape=jinja2.select_autoescape(['html', ]))
    html = env.get_template('registration.mail.html').render(link=link, manual_link=manual_link, token=token)
    text = env.get_template('registration.mail.txt').render(link=link, manual_link=manual_link, token=token)
    send_mail(
        subject="Supernova - Ativação de conta",
        from_email=settings.EMAIL_HOST_FROM,
        recipient_list=(registration.email,),
        message=text,
        html_message=html)
