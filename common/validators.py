from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class DigitValidator(validators.RegexValidator):
    regex = r'^\d+$'
    message = "فقط عدد قابل قبول است."
    flags = 0

__all__ = ('DigitValidator',)