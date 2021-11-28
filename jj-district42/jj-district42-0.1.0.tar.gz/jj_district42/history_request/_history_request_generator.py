from typing import Any, cast

from blahblah import Generator
from district42 import GenericSchema
from jj.mock import HistoryRequest

from ._history_request_schema import HistoryRequestSchema

__all__ = ("HistoryRequestGenerator",)


class HistoryRequestGenerator(Generator, extend=True):
    def visit_jj_history_request(self, schema: HistoryRequestSchema,
                                 **kwargs: Any) -> HistoryRequest:
        generated = {}
        for key in schema.props:
            sch = cast(GenericSchema, schema.props.get(key))
            generated[key] = sch.__accept__(self, **kwargs)
        return HistoryRequest(**generated)
