from typing import Any, Mapping, cast

from district42 import Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42 import schema
from district42.types import AnySchema, Schema
from district42_exp_types.ci_multi_dict import CIMultiDictSchema
from niltype import Nil, Nilable

__all__ = ("HistoryResponseSchema", "HistoryResponseProps",)


class HistoryResponseProps(Props):
    def __init__(self, registry: Nilable[Mapping[str, Any]] = Nil) -> None:
        if registry is Nil:
            registry = {
                "status": schema.int.min(1),
                "reason": schema.str,
                "headers": CIMultiDictSchema(),
                "body": schema.any
            }
        super().__init__(registry)

    @property
    def status(self) -> Nilable[int]:
        return self.get("status")

    @property
    def reason(self) -> Nilable[str]:
        return self.get("reason")

    @property
    def headers(self) -> Nilable[CIMultiDictSchema]:
        return self.get("headers")

    @property
    def body(self) -> Nilable[AnySchema]:
        return self.get("body")


class HistoryResponseSchema(Schema[HistoryResponseProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_jj_history_response(self, **kwargs))
