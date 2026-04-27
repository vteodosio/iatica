from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class ProfessorRegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    email = forms.EmailField(label='E-mail')
    escola = forms.CharField(label='Escola', max_length=200)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'escola', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.PROFESSOR
        user.email = self.cleaned_data['email']
        user.escola = self.cleaned_data['escola']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
