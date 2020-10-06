import random
import string

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

import college.models as college
import users.models as users
import settings
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
    registration = users.Registration.objects.filter(email=email).prefetch_related('invites')
    if registration.exists():
        registration = registration.order_by('creation').reverse().first()
    else:
        raise ExpiredRegistration('Não foi possível encontrar um registo com este email.')

    if registration.token != token:  # Incorrect token
        if registration.failed_attempts < settings.REGISTRATIONS_ATTEMPTS_TOKEN - 1:
            registration.failed_attempts += 1
            registration.save()
            raise InvalidToken()
        else:
            raise InvalidToken(deleted=True)

    # Failure conditions
    # TODO write test for them
    if users.User.objects.filter(username=registration.username).exists():
        raise AccountExists(f"Entretanto registou-se um utilizador com o nome {registration.username}."
                            "É necessário um novo registo.")

    # TODO perhaps replace the nickname with the username to avoid failing in this case:
    if users.User.objects.filter(nickname=registration.nickname).exists():
        if registration.invites.exists():
            registration.invites.first()
        raise AccountExists(f"Entretanto registou-se um utilizador com a alcunha '{registration.nickname}'."
                            "É necessário um novo registo.")

    if users.User.objects.filter(email=registration.email).exists():
        raise AccountExists(f'Foi validada outra conta com o email {registration.email}.')

    if college.Student.objects.filter(abbreviation=registration.student, user__isnull=False).exists():
        raise AccountExists(f'Já foi criada uma conta com o identificador de estudante deste registo.')

    if registration.failed_attempts > settings.REGISTRATIONS_ATTEMPTS_TOKEN:
        raise ExpiredRegistration("Já tentou validar este registo demasiadas vezes.")

    elapsed_minutes = (timezone.now() - registration.creation).seconds / 60
    if elapsed_minutes > settings.REGISTRATIONS_TIMEWINDOW:
        raise ExpiredRegistration('O registo foi validado após o tempo permitido.')

    with transaction.atomic():
        user = users.User.objects.create_user(
            username=registration.username,
            email=registration.email,
            nickname=registration.nickname,
            last_activity=timezone.now()
        )
        user.password = registration.password  # Copy hash
        user.save()
        students = college.Student.objects.filter(abbreviation=registration.student).all()
        for student in students:
            student.user = user
            student.save()
        if len(students) > 0:
            permission = Permission.objects.get(
                codename='full_student_access',
                content_type=ContentType.objects.get_for_model(users.User))
            user.user_permissions.add(permission)
        user.calculate_missing_info()
        user.updated_cached()
        awarded = False
        if len(students) == 1:
            student = students[0]
            if student.first_year == settings.COLLEGE_YEAR:
                offset = users.ReputationOffset.objects.create(amount=10, user=user, reason='Prémio para caloiros :)')
                offset.issue_notification()
        user_count = users.User.objects.count()
        if user_count < 100:
            offset = users.ReputationOffset.objects.create(amount=1000, user=user, reason='Primeiros 100 utilizadores')
            offset.issue_notification()
            awarded = True
        elif user_count < 1000:
            offset = users.ReputationOffset.objects.create(amount=500, user=user, reason='Primeiros 1000 utilizadores')
            offset.issue_notification()
            awarded = True

        if awarded:
            calculate_points(user)
            award_user(user)
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
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=(registration.email,),
        message=text,
        html_message=html)
