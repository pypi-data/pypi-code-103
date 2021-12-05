from typing import Any, cast

from district42 import Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.errors import (
    DeclarationError,
    make_already_declared_error,
    make_incorrect_max_error,
    make_incorrect_min_error,
    make_invalid_type_error,
)
from district42.types import Schema
from niltype import Nil, Nilable

__all__ = ("NumericSchema", "NumericProps",)


class NumericProps(Props):
    @property
    def value(self) -> Nilable[str]:
        return self.get("value")

    @property
    def min(self) -> Nilable[int]:
        return self.get("min")

    @property
    def max(self) -> Nilable[int]:
        return self.get("max")


class NumericSchema(Schema[NumericProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_numeric(self, **kwargs))

    def __call__(self, /, value: str) -> "NumericSchema":
        if not isinstance(value, str):
            raise make_invalid_type_error(self, value, (str,))

        if self.props.value is not Nil:
            raise make_already_declared_error(self)

        if (self.props.min is not Nil) or (self.props.max is not Nil):
            raise make_already_declared_error(self)

        try:
            int(value)
        except (TypeError, ValueError) as e:
            raise DeclarationError(str(e)) from None

        return self.__class__(self.props.update(value=value))

    def min(self, /, value: int) -> "NumericSchema":
        if not isinstance(value, int):
            raise make_invalid_type_error(self, value, (int,))

        if self.props.min is not Nil:
            raise make_already_declared_error(self)

        if (self.props.value is not Nil) and (value > int(self.props.value)):
            raise make_incorrect_min_error(self, self.props.value, value)

        return self.__class__(self.props.update(min=value))

    def max(self, /, value: int) -> "NumericSchema":
        if not isinstance(value, int):
            raise make_invalid_type_error(self, value, (int,))

        if self.props.max is not Nil:
            raise make_already_declared_error(self)

        if (self.props.value is not Nil) and (value < int(self.props.value)):
            raise make_incorrect_max_error(self, self.props.value, value)

        return self.__class__(self.props.update(max=value))
