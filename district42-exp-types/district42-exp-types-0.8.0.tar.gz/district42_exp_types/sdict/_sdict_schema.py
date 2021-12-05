from typing import Any, Dict, cast

from district42 import GenericSchema, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.types import DictSchema
from district42.utils import TypeOrEllipsis

from ._rollout import rollout

__all__ = ("SDictSchema",)


class SDictSchema(DictSchema):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_sdict(self, **kwargs))

    def __call__(self, /, keys: Dict[Any, TypeOrEllipsis[GenericSchema]]) -> "SDictSchema":
        updated_keys = rollout(keys)
        for key, val in updated_keys.items():
            updated_keys[key] = self.__class__()(val) if isinstance(val, dict) else val
        return cast(SDictSchema, super().__call__(updated_keys))
