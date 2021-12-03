from typing import Any, Optional
from django.db import models


__all__ = 'DEFAULT_CODES_FIELD', 'CodeSeeker',


DEFAULT_CODES_FIELD = 'codes'
DEFAULT_CODES_SET_FIELD = 'codes_set'


def s_default(self, name: str, value = None):
    return getattr(self, name, None) if value is None else value


class CodeSeeker:
    name: str
    field_name: str = DEFAULT_CODES_FIELD
    set_field_name: str = DEFAULT_CODES_SET_FIELD

    def __init__(
        self,
        *_,
        name: Optional[str] = None,
        field_name: Optional[str] = None,
        set_field_name: Optional[str] = None,
    ):
        self.name = s_default(self, 'name', name)
        self.field_name = s_default(self, 'field_name', field_name)
        self.set_field_name = s_default(self, 'set_field_name', set_field_name)

    def to_representation(self, value):
        """Function that resolves stored value to a python value type."""
        return value

    def to_value(self, representation):
        """Function that resolves python value type to value that will be
        stored.
        """
        return representation

    def Q_set(self, value: Any, field_name: Optional[str] = None, lookup: str = 'exact') -> models.Q:
        return models.Q(**{
            f'{field_name or self.set_field_name}__code': self.name,
            f'{field_name or self.set_field_name}__value__{lookup}': value
        })

    def Q_json(self, value: Any, field_name: Optional[str] = None) -> models.Q:
        return models.Q(**{
            f'{field_name or self.field_name}__contains': {self.name: [value]}
        })

    def eq(self, a: Any, b: Any) -> bool:
        return self.to_value(a) == self.to_value(b)

    def ge(self, a: Any, b: Any) -> bool:
        return self.to_value(a) > self.to_value(b)

    def __hash__(self) -> int:
        return self.name.__hash__()


