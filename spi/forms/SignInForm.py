from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        label='E-mail ou usuário',
        widget=forms.TextInput(attrs={
            'autocomplete': 'username',
            'autofocus': True,
            'placeholder': 'E-mail ou usuário',
        }),
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Senha',
        }),
    )

    def clean(self):
        identifier = self.cleaned_data.get('username', '').strip()
        if '@' in identifier:
            username = (
                get_user_model().objects
                .filter(email__iexact=identifier)
                .values_list('username', flat=True)
                .first()
            )
            if username:
                self.cleaned_data['username'] = username
        return super().clean()
