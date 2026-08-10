from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError


class AdminEmailOrUsernameAuthenticationForm(AdminAuthenticationForm):
    """Admin login form that accepts the default username or a unique email."""

    username = forms.CharField(
        label="نام کاربری یا ایمیل",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "dir": "ltr",
                "placeholder": "username@example.com",
                "class": "admin-login-input",
            }
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "رمز عبور خود را وارد کنید",
                "class": "admin-login-input",
            }
        ),
    )

    error_messages = {
        "invalid_login": "اطلاعات ورود معتبر نیست یا دسترسی مدیریت برای این حساب فعال نشده است.",
        "inactive": "اطلاعات ورود معتبر نیست یا دسترسی مدیریت برای این حساب فعال نشده است.",
    }

    def clean(self):
        identifier = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if identifier is not None and password:
            username = self._resolve_username(identifier)
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def _resolve_username(self, identifier):
        if "@" not in identifier:
            return identifier

        UserModel = get_user_model()
        users = UserModel._default_manager.filter(email__iexact=identifier)
        if users.count() != 1:
            return identifier
        return users[0].get_username()

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
        )
