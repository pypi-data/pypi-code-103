from enum import Enum
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder


__all__ = 'json_encoder',


django_encoder = DjangoJSONEncoder()


def json_encoder(e):
    if isinstance(e, set):
        return list(e)
    if isinstance(e, Enum):
        return str(e)
    else:
        return django_encoder.default(e)
