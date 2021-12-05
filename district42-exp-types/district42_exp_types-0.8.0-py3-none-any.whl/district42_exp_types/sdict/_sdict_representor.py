from typing import Any

from district42.representor import Representor

from ._sdict_schema import SDictSchema

__all__ = ("SDictRepresentor",)


class SDictRepresentor(Representor, extend=True):
    def visit_sdict(self, schema: SDictSchema, *, indent: int = 0, **kwargs: Any) -> str:
        r = self.visit_dict(schema, indent=indent, **kwargs)
        # dirty, but who cares
        prefix = f"{self._name}.dict"
        return f"{self._name}.sdict" + r[len(prefix):]
