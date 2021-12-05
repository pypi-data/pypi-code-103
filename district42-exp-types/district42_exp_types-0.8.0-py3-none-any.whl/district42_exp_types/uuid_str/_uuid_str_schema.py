from typing import Any, cast
from uuid import UUID

from district42 import Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.errors import (
    DeclarationError,
    make_already_declared_error,
    make_invalid_type_error,
)
from district42.types import Schema
from niltype import Nil, Nilable

__all__ = ("UUIDStrSchema", "UUIDStrProps",)


class UUIDStrProps(Props):
    @property
    def value(self) -> Nilable[str]:
        return self.get("value")

    @property
    def is_lowercase(self) -> Nilable[bool]:
        return self.get("is_lowercase")

    @property
    def is_uppercase(self) -> Nilable[bool]:
        return self.get("is_uppercase")


class UUIDStrSchema(Schema[UUIDStrProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_uuid_str(self, **kwargs))

    def __call__(self, /, value: str) -> "UUIDStrSchema":
        if not isinstance(value, str):
            raise make_invalid_type_error(self, value, (str,))

        try:
            UUID(value)
        except ValueError as e:
            raise DeclarationError(str(e)) from None

        if self.props.value is not Nil:
            raise make_already_declared_error(self)

        return self.__class__(self.props.update(value=value))

    def lowercase(self) -> "UUIDStrSchema":
        if (self.props.value is not Nil) and not (self.props.value.islower()):
            raise make_already_declared_error(self)

        if (self.props.is_lowercase is not Nil) or (self.props.is_uppercase is not Nil):
            raise make_already_declared_error(self)

        return self.__class__(self.props.update(is_lowercase=True))

    def uppercase(self) -> "UUIDStrSchema":
        if (self.props.value is not Nil) and (not self.props.value.isupper()):
            raise make_already_declared_error(self)

        if (self.props.is_uppercase is not Nil) or (self.props.is_lowercase is not Nil):
            raise make_already_declared_error(self)

        return self.__class__(self.props.update(is_uppercase=True))
