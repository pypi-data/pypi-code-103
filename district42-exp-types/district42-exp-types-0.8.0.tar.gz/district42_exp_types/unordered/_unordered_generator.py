from typing import Any, List

from blahblah import Generator

from ._unordered_schema import UnorderedSchema

__all__ = ("UnorderedGenerator",)


class UnorderedGenerator(Generator, extend=True):
    def visit_unordered(self, schema: UnorderedSchema, **kwargs: Any) -> List[Any]:
        res = self.visit_list(schema, **kwargs)
        self._random.shuffle_list(res)
        return res
