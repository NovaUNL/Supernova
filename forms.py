from captcha.fields import CaptchaField
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Utilizador', max_length=100, required=True)
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(),
                               required=False)
    remember = forms.BooleanField(label='Lembrar', required=False)


class AccountCreationForm(forms.Form):
    clip = forms.CharField(label='Identificador do CLIP', max_length=30, required=True)
    nickname = forms.CharField(label='Alcunha (alteravel posteriormente)', max_length=100, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Opcional'}))
    password = forms.CharField(label='Palavra passe', widget=forms.PasswordInput(), required=True)
    password_confirmation = forms.CharField(label='Palavra passe(confirmação)', widget=forms.PasswordInput(),
                                            required=True)
    captcha = CaptchaField(label='Ser bot ou não ser, eis a questão...')
