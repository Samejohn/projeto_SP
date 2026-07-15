from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nome completo',
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'Nome completo'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'E-mail'}),
    )
    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Senha'}),
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirme a senha'}),
    )

    class Meta:
        model = get_user_model()
        fields = ('full_name', 'email', 'password1', 'password2')

    def clean_email(self):
        user_model = get_user_model()
        email = self.cleaned_data['email'].strip().lower()
        username_max_length = user_model._meta.get_field('username').max_length

        if len(email) > username_max_length:
            raise forms.ValidationError(
                f'O e-mail deve ter no máximo {username_max_length} caracteres.'
            )

        email_in_use = user_model.objects.filter(email__iexact=email).exists()
        username_in_use = user_model.objects.filter(username__iexact=email).exists()
        if email_in_use or username_in_use:
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].strip()
        first_name, separator, last_name = full_name.partition(' ')
        user.first_name = first_name
        user.last_name = last_name if separator else ''
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
