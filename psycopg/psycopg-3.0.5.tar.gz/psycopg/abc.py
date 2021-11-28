"""
Protocol objects representing different implementations of the same classes.
"""

# Copyright (C) 2020-2021 The Psycopg Team

from typing import Any, Callable, Generator, Mapping
from typing import List, Optional, Sequence, Tuple, TypeVar, Union
from typing import TYPE_CHECKING

from . import pq
from ._enums import PyFormat as PyFormat
from ._compat import Protocol

if TYPE_CHECKING:
    from .sql import Composable
    from .rows import Row, RowMaker
    from .pq.abc import PGresult
    from .waiting import Wait, Ready
    from .connection import BaseConnection
    from ._adapters_map import AdaptersMap

# An object implementing the buffer protocol
Buffer = Union[bytes, bytearray, memoryview]

Query = Union[str, bytes, "Composable"]
Params = Union[Sequence[Any], Mapping[str, Any]]
ConnectionType = TypeVar("ConnectionType", bound="BaseConnection[Any]")

# TODO: make it recursive when mypy will support it
# DumperKey = Union[type, Tuple[Union[type, "DumperKey"]]]
DumperKey = Union[type, Tuple[type, ...]]

# Waiting protocol types

RV = TypeVar("RV")

PQGenConn = Generator[Tuple[int, "Wait"], "Ready", RV]
"""Generator for processes where the connection file number can change.

This can happen in connection and reset, but not in normal querying.
"""

PQGen = Generator["Wait", "Ready", RV]
"""Generator for processes where the connection file number won't change.

The first item generated is the file descriptor; following items are be the
Wait states.
"""


# Adaptation types

DumpFunc = Callable[[Any], bytes]
LoadFunc = Callable[[bytes], Any]


class AdaptContext(Protocol):
    """
    A context describing how types are adapted.

    Example of `~AdaptContext` are `~psycopg.Connection`, `~psycopg.Cursor`,
    `~psycopg.adapt.Transformer`, `~psycopg.adapt.AdaptersMap`.

    Note that this is a `~typing.Protocol`, so objects implementing
    `!AdaptContext` don't need to explicitly inherit from this class.

    """

    @property
    def adapters(self) -> "AdaptersMap":
        """The adapters configuration that this object uses."""
        ...

    @property
    def connection(self) -> Optional["BaseConnection[Any]"]:
        """The connection used by this object, if available.

        :rtype: `~psycopg.Connection` or `~psycopg.AsyncConnection` or `!None`
        """
        ...


class Dumper(Protocol):
    """
    Convert Python objects of type *cls* to PostgreSQL representation.
    """

    format: pq.Format
    """The format this dumper produces (class attirbute)."""

    oid: int
    """The oid to pass to the server, if known; 0 otherwise (class attribute)."""

    def __init__(self, cls: type, context: Optional[AdaptContext] = None):
        ...

    def dump(self, obj: Any) -> Buffer:
        """Convert the object *obj* to PostgreSQL representation.

        :param obj: the object to convert.
        """
        ...

    def quote(self, obj: Any) -> Buffer:
        """Convert the object *obj* to escaped representation.

        :param obj: the object to convert.
        """
        ...

    def get_key(self, obj: Any, format: PyFormat) -> DumperKey:
        """Return an alternative key to upgrade the dumper to represent *obj*.

        :param obj: The object to convert
        :param format: The format to convert to

        Normally the type of the object is all it takes to define how to dump
        the object to the database. For instance, a Python `~datetime.date` can
        be simply converted into a PostgreSQL :sql:`date`.

        In a few cases, just the type is not enough. For example:

        - A Python `~datetime.datetime` could be represented as a
          :sql:`timestamptz` or a :sql:`timestamp`, according to whether it
          specifies a `!tzinfo` or not.

        - A Python int could be stored as several Postgres types: int2, int4,
          int8, numeric. If a type too small is used, it may result in an
          overflow. If a type too large is used, PostgreSQL may not want to
          cast it to a smaller type.

        - Python lists should be dumped according to the type they contain to
          convert them to e.g. array of strings, array of ints (and which
          size of int?...)

        In these cases, a dumper can implement `!get_key()` and return a new
        class, or sequence of classes, that can be used to indentify the same
        dumper again. If the mechanism is not needed, the method should return
        the same *cls* object passed in the constructor.

        If a dumper implements `get_key()` it should also implmement
        `upgrade()`.

        """
        ...

    def upgrade(self, obj: Any, format: PyFormat) -> "Dumper":
        """Return a new dumper to manage *obj*.

        :param obj: The object to convert
        :param format: The format to convert to

        Once `Transformer.get_dumper()` has been notified by `get_key()` that
        this Dumper class cannot handle *obj* itself, it will invoke
        `!upgrade()`, which should return a new `Dumper` instance, which will
        be reused for every objects for which `!get_key()` returns the same
        result.
        """
        ...


class Loader(Protocol):
    """
    Convert PostgreSQL objects with OID *oid* to Python objects.
    """

    format: pq.Format

    def __init__(self, oid: int, context: Optional[AdaptContext] = None):
        ...

    def load(self, data: Buffer) -> Any:
        """
        Convert the data returned by the database into a Python object.

        :param data: the data to convert.
        """
        ...


class Transformer(Protocol):

    types: Optional[Tuple[int, ...]]
    formats: Optional[List[pq.Format]]

    def __init__(self, context: Optional[AdaptContext] = None):
        ...

    @property
    def connection(self) -> Optional["BaseConnection[Any]"]:
        ...

    @property
    def adapters(self) -> "AdaptersMap":
        ...

    @property
    def pgresult(self) -> Optional["PGresult"]:
        ...

    def set_pgresult(
        self,
        result: Optional["PGresult"],
        *,
        set_loaders: bool = True,
        format: Optional[pq.Format] = None
    ) -> None:
        ...

    def set_dumper_types(
        self, types: Sequence[int], format: pq.Format
    ) -> None:
        ...

    def set_loader_types(
        self, types: Sequence[int], format: pq.Format
    ) -> None:
        ...

    def dump_sequence(
        self, params: Sequence[Any], formats: Sequence[PyFormat]
    ) -> Sequence[Optional[Buffer]]:
        ...

    def get_dumper(self, obj: Any, format: PyFormat) -> Dumper:
        ...

    def load_rows(
        self, row0: int, row1: int, make_row: "RowMaker[Row]"
    ) -> List["Row"]:
        ...

    def load_row(self, row: int, make_row: "RowMaker[Row]") -> Optional["Row"]:
        ...

    def load_sequence(
        self, record: Sequence[Optional[bytes]]
    ) -> Tuple[Any, ...]:
        ...

    def get_loader(self, oid: int, format: pq.Format) -> Loader:
        ...
