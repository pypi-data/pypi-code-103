from typing import Any

from district42 import GenericSchema
from district42.types import Schema

from ._abstract_formatter import AbstractFormatter
from ._formatter import Formatter
from ._validation_result import ValidationResult
from ._validator import Validator
from ._version import version

__version__ = version
__all__ = ("validate", "validate_or_fail", "eq", "Validator", "ValidationResult",
           "ValidationException", "Formatter", "AbstractFormatter",)


_validator = Validator()
_formatter = Formatter()


def validate(schema: GenericSchema, value: Any, **kwargs: Any) -> ValidationResult:
    return schema.__accept__(_validator, value=value, **kwargs)


class ValidationException(Exception):
    pass


def validate_or_fail(schema: GenericSchema, value: Any, **kwargs: Any) -> bool:
    result = validate(schema, value, **kwargs)
    errors = [e.format(_formatter) for e in result.get_errors()]
    if len(errors) == 0:
        return True
    message = "\n - " + "\n - ".join(errors)
    raise ValidationException(message)


def eq(schema: GenericSchema, value: Any) -> bool:
    if isinstance(value, Schema):
        return isinstance(value, schema.__class__) and (schema.props == value.props)
    return not validate(schema, value=value).has_errors()


Schema.__override__(Schema.__eq__.__name__, eq)
