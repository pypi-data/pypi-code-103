from typing import Any, Mapping, cast

from district42 import Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42 import schema
from district42.types import AnySchema, DictSchema, Schema
from district42_exp_types.ci_multi_dict import CIMultiDictSchema
from district42_exp_types.multi_dict import MultiDictSchema
from niltype import Nil, Nilable

__all__ = ("HistoryRequestSchema", "HistoryRequestProps",)


class HistoryRequestProps(Props):
    def __init__(self, registry: Nilable[Mapping[str, Any]] = Nil) -> None:
        if registry is Nil:
            registry = {
                "method": schema.str.len(1, ...),
                "path": schema.str,
                "segments": schema.dict,
                "params": MultiDictSchema(),
                "headers": CIMultiDictSchema(),
                "body": schema.any
            }
        super().__init__(registry)

    @property
    def method(self) -> Nilable[str]:
        return self.get("method")

    @property
    def path(self) -> Nilable[str]:
        return self.get("path")

    @property
    def segments(self) -> Nilable[DictSchema]:
        return self.get("segments")

    @property
    def params(self) -> Nilable[MultiDictSchema]:
        return self.get("params")

    @property
    def headers(self) -> Nilable[CIMultiDictSchema]:
        return self.get("headers")

    @property
    def body(self) -> Nilable[AnySchema]:
        return self.get("body")


class HistoryRequestSchema(Schema[HistoryRequestProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_jj_history_request(self, **kwargs))
