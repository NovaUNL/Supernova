from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import authenticate

from kleep.utils import password_strength
from users.models import User

default_errors = {
    'required': 'Este campo é obrigatório',
    'invalid': 'Foi inserido um valor inválido'
}


class LoginForm(forms.Form):
    username = forms.CharField(label='Utilizador', max_length=100, required=True, error_messages=default_errors)
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(),
                               required=True, error_messages=default_errors)
    remember = forms.BooleanField(label='Lembrar', required=False)  # TODO use me

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


class AccountCreationForm(forms.Form):
    clip = forms.CharField(label='Identificador do CLIP', max_length=30, required=True, error_messages=default_errors)
    nickname = forms.CharField(label='Alcunha (alteravel posteriormente)', max_length=100, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Opcional'}), error_messages=default_errors)
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(), required=True,
                               error_messages=default_errors)
    password_confirmation = forms.CharField(label='Palavra passe(confirmação)', widget=forms.PasswordInput(),
                                            required=True, error_messages=default_errors)
    captcha = CaptchaField(label='Ser bot ou não ser, eis a questão...', error_messages=default_errors)

    def clean_password(self):
        password = self.cleaned_data["new_password"]
        if len(password) < 7:
            raise forms.ValidationError("A palava-passe tem que ter no mínimo 7 carateres.")

        if password_strength(password) < 5:
            raise forms.ValidationError("A password é demasiado fraca.<br>"
                                        "Experimenta misturar maiusculas, minusculas, numeros ou pontuação.")
        return password

    def clean_password_confirmation(self):
        if self.cleaned_data["new_password"] != self.cleaned_data["new_password_confirmation"]:
            raise forms.ValidationError("As palavas-passe não coincidem.")
        return self.cleaned_data["new_password_confirmation"]


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
                                        "Experimenta misturar maiusculas, minusculas, numeros ou pontuação.")
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

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        # TODO
        return self.cleaned_data
