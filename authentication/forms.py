from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from authentication.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='نام کاربری یا ایمیل', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='رمز عبور', strip=False, widget=forms.PasswordInput)
    error_messages = {
        'invalid_login': 'نام کاربری یا رمز عبور اشتباه است. لطفاً دقت کنید.',
        'inactive': 'این حساب کاربری غیرفعال است.',
    }

__all__ = ('UserRegistrationForm', 'CustomAuthenticationForm')