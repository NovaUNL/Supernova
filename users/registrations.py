import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

import clip.models as clip
import users.models as users
import college.clip_synchronization as clip_sync
import settings
from users.exceptions import InvalidToken, InvalidUsername, ExpiredRegistration, AccountExists, AssignedStudent


def pre_register(request, data: users.Registration):
    """
    | Validates and stores registration request data waiting for further confirmation
    | Raises :py:class:`users.exceptions.InvalidUsername` when the asked username matches a student identifier other
        than the requested student.
    | Raises :py:class:`users.exceptions.AccountExists` when the requested username or nickname collides with other
        users or the email is already registered.
    | Raises :py:class:`users.exceptions.AssignedStudent` when the requested student is already bound to an account.

    :param request: Request that originated this call
    :param data: Validated and instantiated ModelForm of a :py:class:`users.Registration` object.
    """
    username = data.username
    nickname = data.nickname
    if clip.Student.objects.filter(abbreviation=username).exclude(id=data.student.id).exists():
        raise InvalidUsername(f'The username {username} matches a CLIP ID.')

    if users.User.objects.filter(Q(username=username) | Q(username=nickname) | Q(nickname=nickname)).exists():
        raise AccountExists(f'There is already an account using the username {username} or the nickname {nickname}.')

    if users.User.objects.filter(email=data.email).exists():
        raise AccountExists(f'There is a registered account with the email {data.email}')

    # Delete any existing registration request for this user
    # Registration.objects.filter(student=data.student).delete()

    if hasattr(data.student, 'student'):
        user = data.student.student.user  # Registration -> clip_student -> student -> user
        if user is not None:
            raise AssignedStudent(f'The student {username} is already assigned to the account {user}.')

    token = generate_token(settings.REGISTRATIONS_TOKEN_LENGTH)
    data.token = token
    send_mail(request, data)
    data.save()


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
    registration = users.Registration.objects.filter(email=email)
    if registration.exists():
        registration = registration.order_by('creation').reverse().first()
    else:
        raise ExpiredRegistration('Não foi possível encontrar um registo com este email.')

    if users.User.objects.filter(username=registration.username).exists():
        raise AccountExists("Utilizador solicitado já foi criado. Se não foi por ti regista um novo.")

    if users.User.objects.filter(email=registration.email).exists():
        raise AccountExists(f'Another account with the email {registration.email} was validated.')

    if registration.failed_attempts > settings.REGISTRATIONS_ATTEMPTS_TOKEN:
        raise ExpiredRegistration("Já tentou validar este registo demasiadas vezes. Faça um novo.")

    if registration.token == token:  # Correct token
        elapsed_minutes = (timezone.now() - registration.creation).seconds / 60
        if elapsed_minutes > settings.REGISTRATIONS_TIMEWINDOW:
            raise ExpiredRegistration('O registo foi validado após o tempo permitido.')

        user = users.User.objects.create_user(
            username=registration.username,
            email=registration.email,
            nickname=registration.nickname,
            last_activity=timezone.now()
        )
        clip_student = registration.student
        user.password = registration.password  # Copy hash
        user.save()
        student = clip_sync.create_student(clip_student)

        if registration.email.endswith('unl.pt'):
            student.confirmed = True

        student.user = user
        student.save()
        return user
    else:
        if registration.failed_attempts < settings.REGISTRATIONS_ATTEMPTS_TOKEN - 1:
            registration.failed_attempts += 1
            registration.save()
            raise InvalidToken()
        else:
            # registration.delete()
            raise InvalidToken(deleted=True)


def generate_token(length: int) -> str:
    """
    Generates a random alphanumeric mixed-case token.
    :param length: Token length
    :return: Token
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def send_mail(request, registration: users.Registration):
    """
    Sends a registration validation email.
    :param request: Request that originated this call
    :param registration: :py:class:`users.models.Registration` for which the email is sent after.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Ativação de conta do Kleep"
    msg['From'] = settings.EMAIL_ACCOUNT
    msg['To'] = registration.email

    # Create the body of the message (a plain-text and an HTML version).
    text = f"""
    Olá. Penso que tentaste criar uma conta no Kleep. Se não foste tu então podes ignorar este email.\n
    Por favor vai a <https://{request.get_host()}{reverse('registration_validation')}> e insere o código {registration.token}.\n
    Este código só é valido na próxima hora.
    """
    html = f"""
    <html>
      <body>
        <p>Olá. Penso que tentaste criar uma conta no Kleep. Se não foste tu então podes ignorar este email.</p>
        <p>Para concluires o registo carrega 
        <a href="https://{request.get_host()}{reverse('registration_validation')}?email={registration.email}&token={registration.token}">aqui</a>.</p>
        <p>Caso o link não seja um link, por favor vai manualmente a https://{request.get_host()}{reverse('registration_validation')}
        e insere o código {registration.token}.</p>
        <p style="font-size:0.8em">Este código só é valido na próxima hora.</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    # TODO async
    server = smtplib.SMTP(settings.EMAIL_SERVER, 587, 30)
    server.ehlo()
    server.starttls()
    server.login(settings.EMAIL_ACCOUNT, settings.EMAIL_PASSWORD)
    server.sendmail(settings.EMAIL_ACCOUNT, registration.email, msg.as_string())
    server.quit()
