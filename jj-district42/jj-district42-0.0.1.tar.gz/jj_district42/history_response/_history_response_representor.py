from typing import Any, cast

from district42.representor import Representor
from district42.types import GenericSchema

from ._history_response_schema import HistoryResponseSchema

__all__ = ("HistoryResponseRepresentor",)


class HistoryResponseRepresentor(Representor, extend=True):
    def visit_jj_history_response(self, schema: HistoryResponseSchema, *,
                                  indent: int = 0, **kwargs: Any) -> str:
        r = f"{self._name}.jj_history_response"

        pairs = []
        for key in schema.props:
            sch = cast(GenericSchema, schema.props.get(key))
            val_repr = sch.__accept__(self, indent=indent + self._indent, **kwargs)
            pairs.append("{indent}{key}={val}".format(
                indent=" " * (indent + self._indent),
                key=key,
                val=val_repr,
            ))

        r += "(<\n"
        r += ",\n".join(pairs) + "\n"
        r += " " * indent + ">)"

        return r
