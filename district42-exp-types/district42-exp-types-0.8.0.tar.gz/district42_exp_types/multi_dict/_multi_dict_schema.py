from typing import Any, Dict, List, Tuple, Union, cast

from district42 import GenericSchema, Props, SchemaVisitor
from district42 import SchemaVisitorReturnType as ReturnType
from district42.errors import make_already_declared_error, make_invalid_type_error
from district42.types import Schema
from multidict import MultiDict, MultiDictProxy
from niltype import Nil, Nilable

__all__ = ("MultiDictProps", "MultiDictSchema",)


MultiDictKeys = Union[
    MultiDict[GenericSchema],
    Dict[str, GenericSchema],
    List[Tuple[str, GenericSchema]],
]


class MultiDictProps(Props):
    @property
    def keys(self) -> Nilable[MultiDict[GenericSchema]]:
        return self.get("keys")


class MultiDictSchema(Schema[MultiDictProps]):
    def __accept__(self, visitor: SchemaVisitor[ReturnType], **kwargs: Any) -> ReturnType:
        return cast(ReturnType, visitor.visit_multi_dict(self, **kwargs))

    def __call__(self, /, keys: MultiDictKeys) -> "MultiDictSchema":
        expected_types = (dict, list, MultiDict, MultiDictProxy)
        if not isinstance(keys, expected_types):
            raise make_invalid_type_error(self, keys, expected_types)

        if self.props.keys is not Nil:
            raise make_already_declared_error(self)

        multidict = MultiDict[GenericSchema]()
        real_keys = keys if isinstance(keys, list) else keys.items()
        for key, val in real_keys:
            if not isinstance(key, str):
                raise make_invalid_type_error(self, key, (str,))
            if not isinstance(val, Schema):
                raise make_invalid_type_error(self, val, (Schema,))
            multidict.add(key, val)

        return self.__class__(self.props.update(keys=multidict))
