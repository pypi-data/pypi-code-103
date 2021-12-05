from typing import Any, cast
from uuid import UUID

from district42 import Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.errors import make_already_declared_error, make_invalid_type_error
from district42.types import Schema
from niltype import Nil, Nilable

__all__ = ("UUIDSchema", "UUIDProps",)


class UUIDProps(Props):
    @property
    def value(self) -> Nilable[UUID]:
        return self.get("value")


class UUIDSchema(Schema[UUIDProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_uuid(self, **kwargs))

    def __call__(self, /, value: UUID) -> "UUIDSchema":
        if not isinstance(value, UUID):
            raise make_invalid_type_error(self, value, (UUID,))

        if self.props.value is not Nil:
            raise make_already_declared_error(self)

        return self.__class__(self.props.update(value=value))
