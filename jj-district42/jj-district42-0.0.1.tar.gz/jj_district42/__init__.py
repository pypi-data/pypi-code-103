from district42 import register_type, schema
from district42_exp_types.uuid_str import UUIDStrSchema

from ._version import version
from .history_request import HistoryRequestSchema
from .history_response import HistoryResponseSchema

register_type("jj_history_request", HistoryRequestSchema)
register_type("jj_history_response", HistoryResponseSchema)

HistoryItemSchema = schema.dict({
    "request": HistoryRequestSchema(),
    "response": HistoryResponseSchema(),
    "tags": schema.list(UUIDStrSchema()),
})

HistorySchema = schema.list(HistoryItemSchema)

__version__ = version
__all__ = ("HistorySchema", "HistoryItemSchema",
           "HistoryRequestSchema", "HistoryResponseSchema",)
