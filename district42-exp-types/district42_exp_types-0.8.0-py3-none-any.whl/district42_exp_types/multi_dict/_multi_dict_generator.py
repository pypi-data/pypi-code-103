from typing import Any

from blahblah import Generator
from district42 import GenericSchema
from multidict import MultiDict
from niltype import Nil

from ._multi_dict_schema import MultiDictSchema

__all__ = ("MultiDictGenerator",)


class MultiDictGenerator(Generator, extend=True):
    def visit_multi_dict(self, schema: MultiDictSchema, **kwargs: Any) -> MultiDict[GenericSchema]:
        generated = MultiDict[GenericSchema]()

        if schema.props.keys is Nil:
            return generated

        for key, val in schema.props.keys.items():
            generated.add(key, val.__accept__(self, **kwargs))

        return generated
