import hashlib
import re

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

import clip.models as clip
from college.models import Student
from kleep.settings import REGISTRATIONS_TOKEN_LENGTH, VULNERABILITY_CHECKING
from kleep.utils import password_strength, correlated
from users.models import User, Registration, VulnerableHash

default_errors = {
    'required': 'Este campo é obrigatório',
    'invalid': 'Foi inserido um valor inválido'
}


class LoginForm(forms.Form):
    username = forms.CharField(label='Utilizador', max_length=100, required=True, error_messages=default_errors)
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(),
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
                raise forms.ValidationError(self.error_messages['invalid_login'])
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.ModelForm):
    password_confirmation = forms.CharField(label='Palavra-passe(confirmação)', widget=forms.PasswordInput(),
                                            required=True, error_messages=default_errors)
    captcha = CaptchaField(label='Como correu Análise?', error_messages=default_errors)
    student = forms.CharField(label='Identificador',
                              widget=forms.TextInput(attrs={'onChange': 'studentIDChanged(this);'}))
    nickname = forms.CharField(label='Alcunha', widget=forms.TextInput(), required=False)

    class Meta:
        model = Registration
        fields = ('nickname', 'username', 'password', 'email', 'student')
        widgets = {
            'username': forms.TextInput(),
            'email': forms.TextInput(attrs={'onChange': 'emailModified=true;'}),
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data["password"]
        if correlated(self.data['username'], password, threshold=0.3):  # TODO magic number to settings
            raise forms.ValidationError("Password demasiado similar à credencial")

        if correlated(self.data['nickname'], password, threshold=0.3):
            raise forms.ValidationError("Password demasiado similar à alcunha")

        if password_strength(password) < 5:
            raise forms.ValidationError("A password é demasiado fraca.<br>"
                                        "Mistura maiusculas, minusculas, numeros e pontuação.")
        if len(password) < 7:
            raise forms.ValidationError("A palava-passe tem que ter no mínimo 7 carateres.")

        if VULNERABILITY_CHECKING:
            sha1 = hashlib.sha1(password.encode()).hexdigest().upper()  # Produces clean SHA1 of the password
            if VulnerableHash.objects.using('vulnerabilities').filter(hash=sha1).exists():
                # Refuse the vulnerable password and tell user about it
                raise forms.ValidationError('Password vulneravel. Espreita a FAQ.')
        password = make_password(password)  # Produces a way stronger hash of the password for storage
        return password

    def clean_password_confirmation(self):
        confirmation = self.cleaned_data["password_confirmation"]
        if self.data["password"] != confirmation:
            raise forms.ValidationError("As palavas-passe não coincidem.")
        return confirmation

    def clean_student(self):
        student_id: str = self.cleaned_data["student"]
        student = clip.Student.objects.filter(abbreviation=student_id)
        if not student.exists():
            raise forms.ValidationError(f"O aluno {student_id} não foi encontrado.")
        if Student.objects.filter(abbreviation=student_id, user__isnull=False).exists():
            raise forms.ValidationError(f"O aluno {student_id} já está registado.")
        return student.first()

    def clean_email(self):
        pattern = re.compile(r'^[\w\d.\-_+]+@[\w\d\-_]+(.[\w\d]+)*(\.\w{2,})$')
        email = self.cleaned_data["email"]
        if not pattern.match(email):
            raise forms.ValidationError("Formato inválido de email.")
        if 'unl.pt' not in email.split('@')[-1]:
            raise forms.ValidationError("Email")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        users = User.objects.filter(username=username)
        if users.exists():
            raise forms.ValidationError(f"Já existe um utilizador com a credencial {username}.")
        users = User.objects.filter(nickname=username)
        if users.exists():
            raise forms.ValidationError(f"Existe um utilizador cuja alcunha é a tua credencial. Escolhe outra.")
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        if nickname is None:
            nickname = self.data["username"]
        users = User.objects.filter(nickname=nickname)
        if users.exists():
            raise forms.ValidationError(f"Já existe um utilizador com a alcunha {nickname}.")
        return nickname


class RegistrationValidationForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=50)
    token = forms.CharField(label='Código', max_length=REGISTRATIONS_TOKEN_LENGTH)

    class Meta:
        model = Registration
        fields = ['email', 'token']

    def clean_token(self):
        token = self.cleaned_data["token"]
        if not token.isalnum():
            raise forms.ValidationError("Invalid token.")
        return token

    def clean_email(self):
        email = self.cleaned_data["email"]
        if re.match(r'^[\w.-]+@[\w]+.[\w.]+$', email) is None:
            raise forms.ValidationError("Invalid email format")
        return email


class AccountSettingsForm(forms.ModelForm):
    password = forms.CharField(label='Palavra-passe atual (confirmação)', widget=forms.PasswordInput(),
                               required=True, error_messages=default_errors)

    class Meta:
        model = User
        fields = ('nickname', 'birth_date', 'residence', 'profile_visibility', 'gender', 'picture', 'webpage')
        widgets = {
            'nickname': forms.TextInput(),
            'residence': forms.TextInput(),
            'webpage': forms.TextInput(),
            'gender': forms.RadioSelect(),
            'picture': forms.FileInput(),
            'birth_date': forms.SelectDateWidget(years=range(1950, 2000))
        }

    def clean_password(self):
        password = self.cleaned_data["password"]
        # TODO
        return password


class PasswordChangeForm(forms.Form):
    password = forms.CharField(label='Nova palavra-passe', widget=forms.PasswordInput(), required=False,
                               error_messages=default_errors)
    password_confirmation = forms.CharField(label='Confirmação', widget=forms.PasswordInput(), required=False,
                                            error_messages=default_errors)

    old_password = forms.CharField(label='Palavra-passe atual', widget=forms.PasswordInput(), required=True,
                                   error_messages=default_errors)

    def clean_old_password(self):
        pass  # TODO

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 7:
            raise forms.ValidationError("A palava-passe tem que ter no mínimo 7 carateres.")

        if password_strength(password) < 5:
            raise forms.ValidationError("A password é demasiado fraca.<br>"
                                        "Mistura maiusculas, minusculas, numeros e pontuação.")
        return password

    def clean_password_confirmation(self):
        password_confirmation = self.cleaned_data["password_confirmation"]
        if self.cleaned_data["password"] != password_confirmation:
            raise forms.ValidationError("As palavas-passe não coincidem.")
        return password_confirmation


class ClipLoginForm(forms.Form):
    username = forms.CharField(label='CLIP ID', max_length=100, required=True)
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(), required=True)

    error_messages = {'invalid_login': "Combinação inválida!"}

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
