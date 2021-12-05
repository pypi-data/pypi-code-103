from typing import Any, cast

from district42 import SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.types import ListSchema

__all__ = ("UnorderedSchema",)


class UnorderedSchema(ListSchema):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_unordered(self, **kwargs))
