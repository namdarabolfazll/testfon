from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from common.validators import DigitValidator
from .validators import PhoneNumberValidator
import typing




# Models
class User(AbstractUser):
    phone_number_validator = PhoneNumberValidator()
    digit_validator = DigitValidator()

    password = models.CharField(_("password"), max_length=128, null=True, blank=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_number_validator])
    balance = models.IntegerField(default=0)
    national_id = models.CharField(max_length=10, null=True, blank=True, validators=[digit_validator])
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'مرد'),
            ('female', 'زن'),
            ('other', 'دیگر'),
        ],
        null=True,
        blank=True,
        verbose_name="جنسیت"
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    address: 'Address'
    # invoices: models.QuerySet['Invoice']

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class State(models.Model):
    name = models.CharField(max_length=128, unique=True)

    cities: models.QuerySet['City']

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'استان {self.name}'


class City(models.Model):
    state = models.ForeignKey(State, models.CASCADE, 'cities')
    name = models.CharField(max_length=128, unique=True)

    addresses: models.QuerySet['Address']

    class Meta:
        ordering = ('state',)

    def __str__(self):
        return f'شهر {self.name} | {self.state}'


class Address(models.Model):
    digit_validator = DigitValidator()

    user = models.OneToOneField(User, models.CASCADE, related_name='address', unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, validators=(digit_validator,), null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, models.CASCADE, 'addresses', null=True, blank=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'آدرس {self.user}'


__all__ = ('User', 'State', 'City', 'Address')
