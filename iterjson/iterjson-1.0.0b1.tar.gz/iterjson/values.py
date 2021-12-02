import abc
from math import inf, nan
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, Union, cast

from iterjson.common import JsonFormatError, _missing, _MissingType

if TYPE_CHECKING:
    from _typeshed import Self

    from iterjson.reader import JsonReader

SimpleJsonType = Union[int, float, str, None]
JsonObjectType = dict[str, 'SupportedJsonType']
JsonArrayType = list['SupportedJsonType']
CollectionJsonType = Union[JsonObjectType, JsonArrayType]
SupportedJsonType = Union[SimpleJsonType, CollectionJsonType]
_T = TypeVar('_T', bound=SupportedJsonType)
_T_simple = TypeVar('_T_simple', bound=SimpleJsonType)
_T_collection = TypeVar('_T_collection', bound=CollectionJsonType)


class JsonValue(abc.ABC, Generic[_T]):
    _first: str
    _reader: 'JsonReader'
    _value: Union[_T, _MissingType]

    def __init__(self, first: str, reader: 'JsonReader') -> None:
        self._first = first
        self._reader = reader
        self._value = _missing

    def _fp_read(self, n: int = 1) -> str:
        return self._reader._read_chars(n)

    @property
    def value(self) -> _T:
        if self._value is _missing:
            self._value = self._read()
        return cast(_T, self._value)

    def read(self) -> _T:
        if self._value is _missing:
            self._value = self._read()
        return cast(_T, self._value)

    @abc.abstractmethod
    def _read(self) -> _T:
        raise NotImplementedError


GenericJsonValue = JsonValue[SupportedJsonType]


class CollectionJsonValue(JsonValue[_T_collection], abc.ABC, Generic[_T_collection]):
    _done: bool
    _current: Any

    def __init__(self, first: str, reader: 'JsonReader') -> None:
        super().__init__(first, reader)
        self._done = False
        self._current = None

    def __iter__(self: 'Self') -> 'Self':
        return self

    @abc.abstractmethod
    def __next__(self) -> Any:
        raise NotImplementedError


GenericCollectionJsonValue = CollectionJsonValue[CollectionJsonType]


class SimpleJsonValue(JsonValue[_T_simple], abc.ABC, Generic[_T_simple]):
    pass


GenericSimpleJsonValue = SimpleJsonValue[SimpleJsonType]


class ObjectValue(CollectionJsonValue[JsonObjectType]):
    _current: tuple[str, GenericJsonValue]

    def __next__(self) -> tuple[str, GenericJsonValue]:
        if self._done:
            raise StopIteration
        if self._current is not None:
            self._current[1].read() # Ensure we've moved on!
        char = self._reader._read_past_whitespace()
        if char == '}':
            self._done = True
            raise StopIteration
        if self._current is not None:
            if char != ',':
                raise JsonFormatError(char)
            self._current = self._read_entry()
        else:
            self._current = self._read_entry(char)
        return self._current

    def _read_entry(self, char: Optional[str] = None) -> tuple[str, GenericJsonValue]:
        if char is None:
            char = self._reader._read_past_whitespace()
        if char != '"':
            raise JsonFormatError(char)
        name = StringValue(char, self._reader).read()
        char = self._reader._read_past_whitespace()
        if char != ':':
            raise JsonFormatError(char)
        return name, self._reader._read_value()

    def _read(self) -> JsonObjectType:
        result: JsonObjectType = {}
        for (key, value) in self:
            result[key] = value.read()
        return result


class ArrayValue(CollectionJsonValue[JsonArrayType]):
    _current: GenericJsonValue

    def __next__(self) -> GenericJsonValue:
        if self._done:
            raise StopIteration
        if self._current is not None:
            self._current.read() # Ensure we've moved on!
        char = self._reader._read_past_whitespace()
        if char == ']':
            self._done = True
            raise StopIteration
        if self._current is not None:
            if char != ',':
                raise JsonFormatError(char)
            self._current = self._reader._read_value()
        else:
            self._current = self._reader._read_value(char)
        return self._current

    def _read(self) -> JsonArrayType:
        result: JsonArrayType = []
        for value in self:
            result.append(value.read())
        if not self._done:
            raise JsonFormatError('EOF')
        return result


_CONTROL_CODES: dict[str, str] = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}

class StringValue(SimpleJsonValue[str]):
    def _read(self) -> str:
        result = ''
        while (c := self._fp_read()) != '"':
            if not c:
                raise JsonFormatError('EOF during string')
            if c == '\\':
                control = self._fp_read()
                if not control:
                    raise JsonFormatError('EOF during string escape')
                elif control == 'u':
                    uni = self._fp_read(4)
                    if len(uni) < 4:
                        raise JsonFormatError('EOF during unicode escape')
                    result += chr(int(uni, 16))
                else:
                    escape = _CONTROL_CODES.get(control)
                    if escape is None:
                        raise JsonFormatError(control)
                    result += escape
                continue
            result += c
        return result


_JsonNumber = Union[int, float]

_DIGITS = '0123456789'

class NumberValue(SimpleJsonValue[_JsonNumber]):
    def _read(self) -> _JsonNumber:
        if self._first == 'N':
            if (s := self._fp_read(2)) != 'aN':
                raise JsonFormatError(s)
            return nan
        if self._first == '-':
            sign = -1
            char = self._fp_read()
        else:
            sign = 1
            char = self._first
        if char == 'I':
            if (s := self._fp_read(7)) != 'nfinity':
                raise JsonFormatError(s)
            return inf * sign
        result = ''
        use_float = False
        if char != '0':
            if not char in _DIGITS:
                raise JsonFormatError(char)
            while True:
                result += char
                char = self._fp_read()
                if not char or char not in _DIGITS:
                    break
        else:
            result = '0'
            char = self._fp_read()
        if char == '.':
            use_float = True
            while True:
                result += char
                char = self._fp_read()
                if not char or char not in _DIGITS:
                    break
            if result[-1] == '.':
                raise JsonFormatError('Trailing decimal point in number')
        if char in 'eE':
            use_float = True
            result += char
            char = self._fp_read()
            if char not in _DIGITS + '-+':
                raise JsonFormatError('Exponential notation missing exponent')
            while True:
                result += char
                char = self._fp_read()
                if not char or char not in _DIGITS:
                    break
        self._reader._buffer = char
        return (float(result) if use_float else int(result)) * sign


_JsonConstant = Union[None, bool]

_CONSTANT_REQUIRES: dict[str, tuple[str, _JsonConstant]] = {
    'n': ('ull', None),
    't': ('rue', True),
    'f': ('alse', False),
}

class ConstantValue(SimpleJsonValue[_JsonConstant]):
    def _read(self) -> _JsonConstant:
        req, val = _CONSTANT_REQUIRES[self._first]
        if (s := self._fp_read(len(req))) != req:
            raise JsonFormatError(s)
        return val
