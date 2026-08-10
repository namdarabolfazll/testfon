from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

# Validators
@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    regex = r'^09\d{9}$'
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @/./+/-/_ characters."
    )
    flags = 0

__all__ = ('PhoneNumberValidator',)
