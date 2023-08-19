from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phonenumber(value: str):
    """ A function to valide user's phone number """
    if value.startswith("+"):
        expected_digits: str = value[1:]
    else:
        expected_digits: str = value
    if (
        (not value)
        or (not expected_digits.isnumeric())
        or len(value) < 10
        or len(value) > 14
    ):
        raise ValidationError(
            _("%(value)s is not a valid phone number"), params={"value": value}
        )

class CustomUser(AbstractUser):
    class TokenReason(models.TextChoices):
        EMAILVERIFICATION = "EmailVerification"

    phone_number = models.CharField(
        max_length=14,
        unique=True,
        db_index=True,
        blank=False, 
    )
    activation_otp = models.CharField(max_length=6, blank=True)
    token = models.CharField(
        max_length=6,
        blank=True,
    )
    token_reason = models.CharField(
        max_length=100,
        blank=True,
    )
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["password"]


    def __str__(self) -> str:
        return self.phone_number

    def save(self, *args, **kwargs):
        if (
            not self.is_active
            and not self.activation_otp
            or not self.activation_otp.isdigit()
        ):
            self.activation_otp = "".join(
                [random.choice("0123456789") for i in range(4)]
            )
        if not self.username and self.phone_number:
            self.username = self.phone_number
        super().save(*args, **kwargs)
