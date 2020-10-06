import hashlib
import re
from datetime import datetime

from django import forms as djf
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

import settings
from college import models as college
from settings import REGISTRATIONS_TOKEN_LENGTH, VULNERABILITY_CHECKING
from supernova.fields import NativeSplitDateTimeField
from supernova.utils import password_strength, correlation
from supernova.widgets import SliderInput, NativeTimeInput
from users import models as m
from learning import models as learning
from settings import CAMPUS_EMAIL_SUFFIX

IDENTIFIER_EXP = re.compile('(?!^\d+$)^[\da-zA-Z-_.]+$')

default_errors = {
    'required': 'Este campo é obrigatório',
    'invalid': 'Foi inserido um valor inválido'
}


class LoginForm(djf.Form):
    username = djf.CharField(label='Utilizador', max_length=100, required=True, error_messages=default_errors)
    password = djf.CharField(label='Palavra passe', widget=djf.PasswordInput(),
                             required=True, error_messages=default_errors)

    error_messages = {
        'invalid_login': "Combinação inválida!",
        'inactive': "Esta conta foi suspensa."}

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise djf.ValidationError(self.error_messages['invalid_login'])
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise djf.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache


class RegistrationForm(djf.ModelForm):
    password_confirmation = djf.CharField(
        label='Palavra-passe (confirmação)',
        widget=djf.PasswordInput(),
        required=True,
        error_messages=default_errors)
    # captcha = CaptchaField(label='Como correu Análise?', error_messages=default_errors)
    student = djf.CharField(
        label='Identificador (ex. c.pereira)',
        widget=djf.TextInput(attrs={'onChange': 'studentIDChanged(this);'}))
    nickname = djf.CharField(label='Alcunha', widget=djf.TextInput(), required=False)
    invite = djf.CharField(required=True)

    class Meta:
        model = m.Registration
        fields = ('nickname', 'username', 'password', 'email', 'student')
        widgets = {
            'username': djf.TextInput(),
            'email': djf.TextInput(attrs={'onChange': 'emailModified=true;'}),
            'password': djf.PasswordInput()
        }

    def clean_password(self):
        return make_password(self.cleaned_data["password"])

    def clean_password_confirmation(self):
        confirmation = self.cleaned_data["password_confirmation"]
        if self.data["password"] != confirmation:
            raise djf.ValidationError("As palavas-passe não coincidem.")
        return confirmation

    def clean_student(self):
        student_id: str = self.cleaned_data["student"].strip()
        students = college.Student.objects.filter(abbreviation=student_id).all()
        if not students.exists():
            raise djf.ValidationError(f"O aluno {student_id} não foi encontrado.")
        elif students.filter(user__isnull=False).exists():
            raise djf.ValidationError(f"O aluno {student_id} já está registado.")
        return student_id

    def clean_email(self):
        pattern = re.compile(r'^[\w\d.\-_+]+@[\w\d\-_]+(.[\w\d]+)*(\.\w{2,})$')
        email = self.cleaned_data["email"]
        student_id = self.data["student"]
        if not pattern.match(email):
            raise djf.ValidationError("Formato inválido de email.")
        prefix, suffix = email.split('@')
        if CAMPUS_EMAIL_SUFFIX not in suffix:
            raise djf.ValidationError(f"Só são aceites emails {CAMPUS_EMAIL_SUFFIX}")
        if student_id != prefix:
            raise djf.ValidationError("Este email não parece pertencer ao identificador indicado.")

        if m.User.objects.filter(email=email).exists():
            raise djf.ValidationError("Já existe uma conta registada com o email fornecido.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        enforce_name_policy(username)
        if m.User.objects.filter(username=username).exists():
            raise djf.ValidationError(f"Já existe um utilizador com o nome de utilizador '{username}'.")
        if m.User.objects.filter(nickname=username).exists():
            raise djf.ValidationError(f"Já existe um utilizador com a alcunha '{username}'")
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        enforce_name_policy(nickname)
        if m.User.objects.filter(username=nickname).exists():
            raise djf.ValidationError(f"Já existe um utilizador com o nome de utilizador '{nickname}'.")
        if m.User.objects.filter(nickname=nickname).exists():
            raise djf.ValidationError(f"Já existe um utilizador com a alcunha '{nickname}'")
        return nickname

    def clean_invite(self):
        if 'invite' not in self.cleaned_data or self.cleaned_data['invite'].strip() == '':
            raise djf.ValidationError("O código de convite não foi preenchido.")
        token = self.cleaned_data["invite"]
        invite = m.Invite.objects.filter(token=token).first()
        if invite is None:
            raise djf.ValidationError("Convite inexistente.")
        if invite.revoked:
            raise djf.ValidationError("Convite anulado.")
        if invite.registration:
            raise djf.ValidationError("Convite já utilizado.")
        if invite.expiration.replace(tzinfo=None) < datetime.now():
            raise djf.ValidationError("Convite caducado.")
        return invite

    def clean(self):
        if not ({'student', 'email', 'username', 'nickname'} <= set(self.cleaned_data)):
            raise djf.ValidationError("Alguns dos campos contem erros")

        student_abbreviation = self.cleaned_data.get("student")
        email_prefix = self.cleaned_data.get("email").split('@')[0]
        nickname = self.cleaned_data.get("nickname")
        username = self.cleaned_data.get("username")

        if student_abbreviation != email_prefix:
            raise djf.ValidationError("Suspeitamos que este email não pertence a este identificador.")

        matching_students = college.Student.objects \
            .filter(Q(abbreviation=email_prefix) | Q(abbreviation=nickname) | Q(abbreviation=username)) \
            .all()

        for student in matching_students:
            if student.user is not None or student.abbreviation != email_prefix:
                raise djf.ValidationError("O email utilizado pertence a outro estudante.")
        enforce_password_policy(
            self.cleaned_data["username"],
            self.cleaned_data["nickname"],
            self.data["password"])
        return self.cleaned_data


class RegistrationValidationForm(djf.ModelForm):
    email = djf.CharField(label='Email', max_length=50)
    token = djf.CharField(label='Código', max_length=REGISTRATIONS_TOKEN_LENGTH)

    class Meta:
        model = m.Registration
        fields = ['email', 'token']

    def clean_token(self):
        token = self.cleaned_data["token"]
        if not token.isalnum():
            raise djf.ValidationError("Invalid token.")
        return token

    def clean_email(self):
        email = self.cleaned_data["email"]
        if re.match(r'^[\w.-]+@[\w]+.[\w.]+$', email) is None:
            raise djf.ValidationError("Invalid email format")
        return email


class UserForm(djf.ModelForm):
    class Meta:
        fields = ('username', 'nickname', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                  'last_login', 'last_nickname_change', 'birth_date', 'gender',
                  'profile_visibility', 'info_visibility', 'about_visibility', 'social_visibility',
                  'groups_visibility', 'enrollments_visibility', 'schedule_visibility',
                  'residence', 'picture', 'webpage', 'about', 'is_student', 'is_teacher', 'course', 'points')
        model = m.User


class AccountSettingsForm(djf.ModelForm):
    new_password = djf.CharField(widget=djf.PasswordInput(), required=False, error_messages=default_errors)
    new_password_confirmation = djf.CharField(widget=djf.PasswordInput(), required=False,
                                              error_messages=default_errors)
    old_password = djf.CharField(widget=djf.PasswordInput(), required=True, error_messages=default_errors)

    class Meta:
        model = m.User
        fields = ('nickname', 'birth_date', 'residence', 'gender', 'picture', 'webpage', 'about',
                  'profile_visibility', 'info_visibility', 'about_visibility', 'social_visibility', 'groups_visibility',
                  'enrollments_visibility', 'schedule_visibility')
        widgets = {
            'gender': djf.RadioSelect(),
            'picture': djf.FileInput(),
            'birth_date': djf.SelectDateWidget(years=range(1950, 2005))
        }

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        if self.instance.nickname == nickname:
            return nickname

        days_since_change = (datetime.now().date() - self.instance.last_nickname_change).days
        if days_since_change < 180:
            raise djf.ValidationError(f"Mudou a sua alcunha há menos de 6 meses (passaram {days_since_change} dias)")
        enforce_name_policy(nickname)

        if m.User.objects \
                .exclude(id=self.instance.id) \
                .filter(Q(username=nickname) | Q(nickname=nickname)) \
                .exists():
            raise djf.ValidationError(f"A alcunha '{nickname}' está a uso.")
        if college.Student.objects.filter(abbreviation=nickname).exclude(user=self.instance).exists():
            raise djf.ValidationError(f"A alcunha '{nickname}' pertence a um estudante")
        return nickname

    def clean_old_password(self):
        if 'old_password' not in self.cleaned_data or self.cleaned_data['old_password'] == '':
            raise djf.ValidationError("A palavra-passe antiga ficou por preencher.")
        if not self.instance.check_password(self.data["old_password"]):
            raise djf.ValidationError("A palavra-passe está incorreta.")

    def clean_new_password(self):
        if 'new_password' not in self.cleaned_data:
            return None
        password = self.cleaned_data['new_password']
        if password.strip() == '':
            return None
        return self.cleaned_data["new_password"]

    def clean_new_password_confirmation(self):
        if "new_password" not in self.cleaned_data:
            if "new_password_confirmation" not in self.cleaned_data:
                raise djf.ValidationError("O campo de nova palavra-passe ficou por preencher.")
            return None

        if "new_password_confirmation" not in self.cleaned_data:
            raise djf.ValidationError("Não foi inserida a palava-passe de confirmação.")

        confirmation = self.cleaned_data["new_password_confirmation"]
        if confirmation == '':
            return None
        return confirmation

    def clean(self):
        if 'new_password' in self.cleaned_data:
            if 'new_password_confirmation' in self.cleaned_data:
                new = self.data["new_password"]
                confirmation = self.data["new_password_confirmation"]
                if new != confirmation:
                    raise djf.ValidationError("A nova palavra-passe não coincide com a confirmação.")
                else:
                    return self.cleaned_data
            else:
                raise djf.ValidationError("A confirmação da nova palava-passe ficou por preencher.")

        if 'new_password_confirmation' in self.cleaned_data:
            raise djf.ValidationError("Foi inserida uma nova palavra-passe mas apenas na confirmação")
        if self.cleaned_data["new_password"] is not None:
            enforce_password_policy(
                self.instance.username,
                self.instance.nickname,
                self.cleaned_data["new_password"])
        return self.cleaned_data


class AccountPermissionsForm(djf.Form):
    can_view_college_data = djf.BooleanField(widget=SliderInput(), required=False)
    can_add_invites = djf.BooleanField(widget=SliderInput(), required=False)
    can_add_synopsis_sections = djf.BooleanField(widget=SliderInput(), required=False)
    can_change_synopsis_sections = djf.BooleanField(widget=SliderInput(), required=False)
    can_add_exercises = djf.BooleanField(widget=SliderInput(), required=False)
    can_change_exercises = djf.BooleanField(widget=SliderInput(), required=False)
    can_change_courses = djf.BooleanField(widget=SliderInput(), required=False)
    can_change_departments = djf.BooleanField(widget=SliderInput(), required=False)
    can_change_teachers = djf.BooleanField(widget=SliderInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        if 'initial' not in kwargs:
            kwargs['initial'] = self.__calc_initial()
        super(AccountPermissionsForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.is_valid():
            raise Exception()

        if self.user.is_staff:
            return

        # field, model, permission
        permissions = [
            ('can_view_college_data', m.User, 'full_student_access'),
            ('can_add_invites', m.Invite, 'add_invite'),
            ('can_add_synopsis_sections', learning.Section, 'add_section'),
            ('can_change_synopsis_sections', learning.Section, 'change_section'),
            ('can_add_exercises', learning.Exercise, 'add_exercise'),
            ('can_change_exercises', learning.Exercise, 'change_exercise'),
            ('can_change_courses', college.Course, 'change_course'),
            ('can_change_departments', college.Department, 'change_department'),
            ('can_change_teachers', college.Teacher, 'change_teacher')
        ]

        for field, model, permission_name in permissions:
            content_type = ContentType.objects.get_for_model(model)
            value = self.cleaned_data[field]
            permission = Permission.objects.get(codename=permission_name, content_type=content_type)
            current = permission in self.user.user_permissions.all()
            if value == current:
                continue
            if value:
                self.user.user_permissions.add(permission)
            else:
                self.user.user_permissions.remove(permission)

    def __calc_initial(self):
        return {
            'can_view_college_data': self.user.has_perm('users.full_student_access'),
            'can_add_synopsis_sections': self.user.has_perm('learning.add_section'),
            'can_change_synopsis_sections': self.user.has_perm('learning.change_section'),
            'can_add_exercises': self.user.has_perm('learning.add_exercise'),
            'can_change_exercises': self.user.has_perm('learning.change_exercise'),
            'can_change_courses': self.user.has_perm('college.change_course'),
            'can_change_departments': self.user.has_perm('college.change_department'),
            'can_change_teachers': self.user.has_perm('college.change_teacher'),
        }


class ScheduleOnceForm(djf.ModelForm):
    datetime = NativeSplitDateTimeField()

    class Meta:
        model = m.ScheduleOnce
        fields = ('title', 'datetime', 'duration')
        widgets = {
            'duration': djf.NumberInput(attrs={'min': 0, 'max': 24 * 60, 'size': 3})
        }


UserScheduleOnceFormset = djf.inlineformset_factory(m.User, m.ScheduleOnce, extra=1, form=ScheduleOnceForm)


class SchedulePeriodicForm(djf.ModelForm):
    start_date = NativeSplitDateTimeField()
    end_date = NativeSplitDateTimeField()

    class Meta:
        model = m.SchedulePeriodic
        fields = ('title', 'weekday', 'time', 'duration', 'start_date', 'end_date')
        widgets = {
            'time': NativeTimeInput(),
            'duration': djf.NumberInput(attrs={'min': 0, 'max': 24 * 60, 'size': 3})
        }


UserSchedulePeriodicFormset = djf.inlineformset_factory(m.User, m.SchedulePeriodic, extra=1, form=SchedulePeriodicForm)


def enforce_name_policy(name):
    if not IDENTIFIER_EXP.fullmatch(name):
        raise djf.ValidationError(f"O nome '{name}' é invalido.")
    if name.lower() in ('admin', 'administrador', 'administração', 'gestor', 'gestão',
                        'regência', 'direção', 'diretor', 'presidente', 'coordenador', 'professor', 'ac'):
        raise djf.ValidationError("Nome de utilizador proibido")


def enforce_password_policy(username, nickname, password):
    if correlation(username, password) > settings.MAX_PASSWORD_CORRELATION:  # TODO magic number to settings
        raise djf.ValidationError("Password demasiado similar à credencial")

    if correlation(nickname, password) > settings.MAX_PASSWORD_CORRELATION:
        raise djf.ValidationError("Password demasiado similar à alcunha")

    if password_strength(password) < 5:
        raise djf.ValidationError("A password é demasiado fraca. "
                                  "Mistura maiusculas, minusculas, numeros e pontuação.")
    if len(password) < 7:
        raise djf.ValidationError("A palava-passe tem que ter no mínimo 7 carateres.")

    if VULNERABILITY_CHECKING:
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()  # Produces clean SHA1 of the password
        if m.VulnerableHash.objects.using('vulnerabilities').filter(hash=sha1).exists():
            # Refuse the vulnerable password and tell user about it
            raise djf.ValidationError('Password vulneravel. Espreita a FAQ.')
