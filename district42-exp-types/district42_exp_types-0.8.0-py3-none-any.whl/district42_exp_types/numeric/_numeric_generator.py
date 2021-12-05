from typing import Any

from blahblah import Generator
from niltype import Nil

from ._numeric_schema import NumericSchema

__all__ = ("NumericGenerator",)

INT_MIN = -(2 ** 63)
INT_MAX = 2 ** 63 - 1


class NumericGenerator(Generator, extend=True):
    def visit_numeric(self, schema: NumericSchema, **kwargs: Any) -> str:
        if schema.props.value is not Nil:
            return schema.props.value

        min_value = INT_MIN
        if schema.props.min is not Nil:
            min_value = int(schema.props.min)

        max_value = INT_MAX
        if schema.props.max is not Nil:
            max_value = int(schema.props.max)

        return str(self._random.random_int(min_value, max_value))
