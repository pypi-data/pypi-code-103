from typing import Any, Dict

from blahblah import Generator

from ._sdict_schema import SDictSchema

__all__ = ("SDictGenerator",)


class SDictGenerator(Generator, extend=True):
    def visit_sdict(self, schema: SDictSchema, **kwargs: Any) -> Dict[str, Any]:
        return self.visit_dict(schema, **kwargs)
