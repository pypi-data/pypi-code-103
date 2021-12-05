from typing import Any

from district42.representor import Representor

from ._unordered_schema import UnorderedSchema

__all__ = ("UnorderedRepresentor",)


class UnorderedRepresentor(Representor, extend=True):
    def visit_unordered(self, schema: UnorderedSchema, *, indent: int = 0, **kwargs: Any) -> str:
        r = self.visit_list(schema, indent=indent, **kwargs)
        # dirty, but who cares
        prefix = f"{self._name}.list"
        return f"{self._name}.unordered" + r[len(prefix):]
