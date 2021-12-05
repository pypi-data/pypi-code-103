from typing import Any
from uuid import UUID, uuid4

from blahblah import Generator
from niltype import Nil

from ._uuid_schema import UUIDSchema

__all__ = ("UUIDGenerator",)


class UUIDGenerator(Generator, extend=True):
    def visit_uuid(self, schema: UUIDSchema, **kwargs: Any) -> UUID:
        if schema.props.value is not Nil:
            return schema.props.value
        return uuid4()
