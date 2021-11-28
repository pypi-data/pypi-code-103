from typing import Any, cast

from district42.types import GenericSchema
from niltype import Nil
from revolt import Substitutor
from revolt.errors import SubstitutionError

from ._history_request_schema import HistoryRequestSchema

__all__ = ("HistoryRequestSubstitutor",)


class HistoryRequestSubstitutor(Substitutor, extend=True):
    def visit_jj_history_request(self, schema: HistoryRequestSchema, *,
                                 value: Any = Nil, **kwargs: Any) -> HistoryRequestSchema:
        if not isinstance(value, dict):
            raise SubstitutionError("Not implemented yet")

        props = {}
        for key in schema.props:
            if key not in value:
                continue
            sch = cast(GenericSchema, schema.props.get(key))
            props[key] = sch.__accept__(self, value=value.get(key), **kwargs)

        for key in value:
            if key not in schema.props:
                raise SubstitutionError(f"Value {value!r} contains extra key {key!r}")

        return schema.__class__(schema.props.update(**props))
