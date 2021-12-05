from typing import Any, cast

from niltype import Nil
from revolt import Substitutor

from ._rollout import rollout
from ._sdict_schema import SDictSchema

__all__ = ("SDictSubstitutor",)


class SDictSubstitutor(Substitutor, extend=True):
    def visit_sdict(self, schema: SDictSchema, *, value: Any = Nil, **kwargs: Any) -> SDictSchema:
        assert isinstance(value, dict)
        return cast(SDictSchema, self.visit_dict(schema, value=rollout(value), **kwargs))
