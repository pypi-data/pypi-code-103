from typing import Any

from district42.representor import Representor
from niltype import Nil

from ._uuid_schema import UUIDSchema

__all__ = ("UUIDRepresentor",)


class UUIDRepresentor(Representor, extend=True):
    def visit_uuid(self, schema: UUIDSchema, *, indent: int = 0, **kwargs: Any) -> str:
        r = f"{self._name}.uuid"

        if schema.props.value is not Nil:
            r += f"({schema.props.value!r})"

        return r
