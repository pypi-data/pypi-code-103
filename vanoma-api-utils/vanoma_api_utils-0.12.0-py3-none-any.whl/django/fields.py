import uuid
from typing import Any
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from vanoma_api_utils.phone_numbers import is_valid_number


class PrimaryKeyField(models.UUIDField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["editable"] = False
        kwargs["primary_key"] = True
        kwargs["default"] = uuid.uuid4
        super().__init__(*args, **kwargs)


class StringField(models.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 150
        super().__init__(*args, **kwargs)


class PhoneNumberField(StringField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["validators"] = [PhoneNumberField.validate_number]
        super().__init__(*args, **kwargs)

    @staticmethod
    def validate_number(phone_number: str) -> None:
        if not is_valid_number(phone_number):
            raise ValidationError(
                _("Phone number {} is not valid.".format(phone_number))
            )
