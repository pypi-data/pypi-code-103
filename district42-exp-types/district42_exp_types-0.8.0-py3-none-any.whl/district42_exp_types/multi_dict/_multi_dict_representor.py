from typing import Any

from district42.representor import Representor
from niltype import Nil

from ._multi_dict_schema import MultiDictSchema

__all__ = ("MultiDictRepresentor",)


class MultiDictRepresentor(Representor, extend=True):
    def visit_multi_dict(self, schema: MultiDictSchema, *, indent: int = 0, **kwargs: Any) -> str:
        r = f"{self._name}.multi_dict"

        if schema.props.keys is Nil:
            return r

        if len(schema.props.keys) == 0:
            return r + "([])"

        pairs = []
        for key, val in schema.props.keys.items():
            key_repr = repr(key)
            val_repr = val.__accept__(self, indent=indent + self._indent, **kwargs)
            pairs.append("{indent}({key}, {val})".format(
                indent=" " * (indent + self._indent),
                key=key_repr,
                val=val_repr,
            ))

        r += "([\n"
        r += ",\n".join(pairs) + "\n"
        r += " " * indent + "])"

        return r
