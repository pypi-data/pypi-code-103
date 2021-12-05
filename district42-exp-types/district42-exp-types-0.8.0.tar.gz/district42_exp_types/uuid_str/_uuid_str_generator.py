from typing import Any
from uuid import uuid4

from blahblah import Generator
from niltype import Nil

from ._uuid_str_schema import UUIDStrSchema

__all__ = ("UUIDStrGenerator",)


class UUIDStrGenerator(Generator, extend=True):
    def visit_uuid_str(self, schema: UUIDStrSchema, **kwargs: Any) -> str:
        if schema.props.value is not Nil:
            return schema.props.value

        generated = str(uuid4())
        if schema.props.is_lowercase:
            return generated.lower()

        if schema.props.is_uppercase:
            return generated.upper()

        # The hexadecimal values "a" through "f" are output as
        # lower case characters and are case insensitive on input.
        # https://www.ietf.org/rfc/rfc4122.txt
        return self._random.random_choice((generated.lower(), generated.upper()))
