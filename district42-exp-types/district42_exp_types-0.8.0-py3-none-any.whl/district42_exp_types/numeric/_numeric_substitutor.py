from typing import Any

from niltype import Nil
from revolt import Substitutor
from revolt.errors import make_substitution_error

from ._numeric_schema import NumericSchema

__all__ = ("NumericSubstitutor",)


class NumericSubstitutor(Substitutor, extend=True):
    def visit_numeric(self, schema: NumericSchema, *,
                      value: Any = Nil, **kwargs: Any) -> NumericSchema:
        result = schema.__accept__(self._validator, value=value)
        if result.has_errors():
            raise make_substitution_error(result, self._formatter)
        return schema.__class__(schema.props.update(value=value))
