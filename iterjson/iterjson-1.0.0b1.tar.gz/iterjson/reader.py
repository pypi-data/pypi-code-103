from os import PathLike
from typing import Any, Optional, TextIO, Union, cast, get_args

from iterjson.common import JsonFormatError, _missing, _MissingType
from iterjson.values import (ArrayValue, ConstantValue, GenericJsonValue,
                             JsonValue, NumberValue, ObjectValue, StringValue)

__all__ = ['JsonReader']

AnyPath = Union[str, bytes, PathLike]

_CHAR_TYPE_MAP: dict[str, type[JsonValue[Any]]] = {
    '{': ObjectValue,
    '[': ArrayValue,

    '"': StringValue,

    'n': ConstantValue,
    't': ConstantValue,
    'f': ConstantValue,
}

for _number_char in '-0123456789IN':
    _CHAR_TYPE_MAP[_number_char] = NumberValue

_WHITESPACE = ' \r\n\t'


class JsonReader:
    _fp: TextIO
    _root: Union[GenericJsonValue, _MissingType]
    _buffer: Optional[str]

    def __init__(self, input: Union[TextIO, AnyPath]) -> None:
        if isinstance(input, get_args(AnyPath)):
            input = open(cast(AnyPath, input), 'rt')
        self._fp = cast(TextIO, input)
        self._root = _missing
        self._buffer = None

    @property
    def root(self) -> GenericJsonValue:
        if self._root is _missing:
            self._root = self._read_value()
        return cast(GenericJsonValue, self._root)

    def __enter__(self) -> 'JsonReader':
        self._fp.__enter__()
        return self

    def __exit__(self, *args) -> Optional[bool]:
        return self._fp.__exit__(*args)

    def _read_chars(self, n: int = 1) -> str:
        if self._buffer:
            result = self._buffer
            self._buffer = None
            if n == 1:
                return result
            return result + self._fp.read(n - 1)
        return self._fp.read(n)

    def _read_value(self, char: Optional[str] = None) -> GenericJsonValue:
        if char is None:
            char = self._read_past_whitespace()
        type = _CHAR_TYPE_MAP.get(char)
        if type is None:
            raise JsonFormatError(char)
        return type(char, self)

    def _read_past_whitespace(self) -> str:
        while (c := self._read_chars()) in _WHITESPACE:
            if c == '':
                raise JsonFormatError('EOF')
        return c
