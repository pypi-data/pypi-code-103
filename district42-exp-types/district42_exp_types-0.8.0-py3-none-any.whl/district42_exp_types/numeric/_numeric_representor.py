from typing import Any

from district42.representor import Representor
from niltype import Nil

from ._numeric_schema import NumericSchema

__all__ = ("NumericRepresentor",)


class NumericRepresentor(Representor, extend=True):
    def visit_numeric(self, schema: NumericSchema, *, indent: int = 0, **kwargs: Any) -> str:
        r = f"{self._name}.numeric"

        if schema.props.value is not Nil:
            r += f"({schema.props.value!r})"

        if schema.props.min is not Nil:
            r += f".min({schema.props.min!r})"

        if schema.props.max is not Nil:
            r += f".max({schema.props.max!r})"

        return r
