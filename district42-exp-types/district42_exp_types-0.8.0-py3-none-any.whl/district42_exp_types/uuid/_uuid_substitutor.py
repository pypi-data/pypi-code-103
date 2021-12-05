from typing import Any

from niltype import Nil
from revolt import Substitutor
from revolt.errors import make_substitution_error

from ._uuid_schema import UUIDSchema

__all__ = ("UUIDSubstitutor",)


class UUIDSubstitutor(Substitutor, extend=True):
    def visit_uuid(self, schema: UUIDSchema, *, value: Any = Nil, **kwargs: Any) -> UUIDSchema:
        result = schema.__accept__(self._validator, value=value)
        if result.has_errors():
            raise make_substitution_error(result, self._formatter)
        return schema.__class__(schema.props.update(value=value))
