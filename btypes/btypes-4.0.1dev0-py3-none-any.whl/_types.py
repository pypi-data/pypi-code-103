from collections import ChainMap, Counter, OrderedDict, abc, defaultdict, deque
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    ByteString,
    Callable,
    Collection,
    Container,
    Coroutine,
    Generator,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MappingView,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Reversible,
    Sequence,
    ValuesView,
)
from typing import (
    Any,
    Final,
    Generic,
    Literal,
    NamedTuple,
    NoReturn,
    Protocol,
    Text,
    TypedDict,
    Union,
)

from typing_extensions import (
    Concatenate,
    ParamSpec,
    ParamSpecArgs,
    ParamSpecKwargs,
    TypeAlias,
)

__all__ = [
    "AbstractSet",
    "Any",
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "Bool",
    "ByteArray",
    "ByteString",
    "Bytes",
    "Callable",
    "ChainMap",
    "Collection",
    "Complex",
    "Concatenate",
    "Container",
    "Coroutine",
    "Counter",
    "Dict",
    "Final",
    "Float",
    "FrozenSet",
    "Generator",
    "Generic",
    "Int",
    "ItemsView",
    "Iterable",
    "Iterator",
    "KeysView",
    "List",
    "Literal",
    "Mapping",
    "MappingView",
    "MutableMapping",
    "MutableSequence",
    "MutableSet",
    "NamedTuple",
    "NoReturn",
    "Object",
    "OrderedDict",
    "ParamSpec",
    "ParamSpecArgs",
    "ParamSpecKwargs",
    "Protocol",
    "Reversible",
    "Sequence",
    "Set",
    "Slice",
    "Str",
    "Str",
    "Text",
    "Tuple",
    "Type",
    "TypeAlias",
    "TypedDict",
    "Union",
    "ValuesView",
]

# builtin types
Bool: TypeAlias = bool
ByteArray: TypeAlias = bytearray
Bytes: TypeAlias = bytes
Complex: TypeAlias = complex
Dict: TypeAlias = dict
Float: TypeAlias = float
FrozenSet: TypeAlias = frozenset
Int: TypeAlias = int
List: TypeAlias = list
Object: TypeAlias = object
Set: TypeAlias = set
Slice: TypeAlias = slice
Str: TypeAlias = str
Tuple: TypeAlias = tuple
Type: TypeAlias = type

# collections
DefaultDict: TypeAlias = defaultdict
Deque: TypeAlias = deque

# abstract base classes
AbstractSet: TypeAlias = abc.Set
