from captcha.fields import CaptchaField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib.auth import authenticate

from kleep.utils import password_strength

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
            raise forms.ValidationError("A palava-chave tem que ter no mínimo 7 carateres.")

        if password_strength(password) < 5:
            raise forms.ValidationError("A password é demasiado fraca.<br>"
                                        "Experimenta misturar maiusculas, minusculas, numeros ou pontuação.")
        return password

    def clean_password_confirmation(self):
        if self.cleaned_data["new_password"] != self.cleaned_data["new_password_confirmation"]:
            raise forms.ValidationError("As palavas-chave não coincidem.")
        return self.cleaned_data["new_password_confirmation"]


class AccountSettingsForm(forms.Form):
    nickname = forms.CharField(label='Alcunha:', max_length=100, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Alcunha'}), error_messages=default_errors)

    CHOICES = [('male', 'Homem'),
               ('female', 'Mulher'),
               ('genderless', 'É complicado')]
    gender = forms.ChoiceField(label='Genero', choices=CHOICES, widget=forms.RadioSelect())

    residency = forms.CharField(label='Residência:', max_length=100, required=False,
                                widget=forms.TextInput(attrs={'placeholder': 'Concelho ou freguesia'}),
                                error_messages=default_errors)

    public_to_users = forms.BooleanField(label='Visível para utilizadores', widget=forms.CheckboxInput(),
                                         required=False, error_messages=default_errors)
    public_to_outsiders = forms.BooleanField(label='Visível para todos', widget=forms.CheckboxInput(), required=False,
                                             error_messages=default_errors)

    gitlab = forms.CharField(label='GitLab:', max_length=100, required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'nickname'}),
                             error_messages=default_errors)
    github = forms.CharField(label='GitHub:', max_length=100, required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'nickname'}),
                             error_messages=default_errors)
    reddit = forms.CharField(label='Reddit:', max_length=100, required=False,
                             widget=forms.TextInput(attrs={'placeholder': '/u/nickname'}),
                             error_messages=default_errors)
    discord = forms.CharField(label='Discord:', max_length=100, required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'nickname#1234'}),
                              error_messages=default_errors)
    linkedin = forms.CharField(label='LinkedIn:', max_length=100, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'nickname'}),
                               error_messages=default_errors)
    twitter = forms.CharField(label='Twitter:', max_length=100, required=False,
                              widget=forms.TextInput(attrs={'placeholder': '@nickname'}),
                              error_messages=default_errors)
    google_plus = forms.CharField(label='Google+:', max_length=100, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': '+nickname'}),
                                  error_messages=default_errors)
    facebook = forms.CharField(label='Facebook:', max_length=100, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'facebook.com/xxxyyyzzz'}),
                               error_messages=default_errors)
    vimeo = forms.CharField(label='Vimeo:', max_length=100, required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'channel'}),
                            error_messages=default_errors)
    youtube = forms.CharField(label='Youtube:', max_length=100, required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'youtube.com/channel/xxxyyyzzz'}),
                              error_messages=default_errors)
    deviantart = forms.CharField(label='DeviantArt:', max_length=100, required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'nickname.deviantart.com'}),
                                 error_messages=default_errors)
    instagram = forms.CharField(label='Instagram:', max_length=100, required=False,
                                widget=forms.TextInput(attrs={'placeholder': 'nickname'}),
                                error_messages=default_errors)
    flickr = forms.CharField(label='Flickr:', max_length=100, required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'flickr.com/photos/xxxyyyzzz/'}),
                             error_messages=default_errors)

    new_password = forms.CharField(label='Nova palavra passe', widget=forms.PasswordInput(), required=False,
                                   error_messages=default_errors)
    new_password_confirmation = forms.CharField(label='Confirmação', widget=forms.PasswordInput(), required=False,
                                                error_messages=default_errors)

    password = forms.CharField(label='Palavra passe atual', widget=forms.PasswordInput(), required=True,
                               error_messages=default_errors)

    def clean_password_confirmation(self):
        if self.cleaned_data["new_password"] != self.cleaned_data["new_password_confirmation"]:
            raise forms.ValidationError("As palavas-chave não coincidem.")
        return self.cleaned_data["new_password_confirmation"]


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


class CreateSynopsisSectionForm(forms.Form):
    name = forms.CharField(label='Título', max_length=100, required=True)
    content = forms.CharField(label='Conteudo:', widget=CKEditorUploadingWidget())
    after = forms.ChoiceField(label='Após:')
