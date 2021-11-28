from typing import Any, cast

from blahblah import Generator
from district42 import GenericSchema
from jj.mock import HistoryResponse

from ._history_response_schema import HistoryResponseSchema

__all__ = ("HistoryResponseGenerator",)


class HistoryResponseGenerator(Generator, extend=True):
    def visit_jj_history_response(self, schema: HistoryResponseSchema,
                                  **kwargs: Any) -> HistoryResponse:
        generated = {}
        for key in schema.props:
            sch = cast(GenericSchema, schema.props.get(key))
            generated[key] = sch.__accept__(self, **kwargs)
        return HistoryResponse(**generated)
