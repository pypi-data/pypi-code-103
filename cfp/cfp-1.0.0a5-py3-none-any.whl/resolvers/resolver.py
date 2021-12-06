from abc import ABC, abstractmethod
from typing import Any, Generic, Iterator, TypeVar, cast

from cfp.sources.source import AnySource, TSource
from cfp.types import ApiParameter, StackParameterKey


class Resolver(ABC, Generic[TSource]):
    """Abstract base resolver."""

    @abstractmethod
    def _queue(self, key: StackParameterKey, source: TSource) -> None:
        """
        Queues a resolution task to perform later.

        Arguments:
            key:    Stack parameter key
            source: Value source
        """

    def queue(self, key: StackParameterKey, source: AnySource) -> None:
        """
        Queues a resolution task to perform later.

        Arguments:
            key:    Stack parameter key
            source: Value source
        """

        self._queue(key=key, source=cast(TSource, source))

    @abstractmethod
    def resolve(self) -> Iterator[ApiParameter]:
        """
        Invokes the queued resolution tasks and returns an iterator of the
        values.
        """


AnyResolver = Resolver[Any]

TResolver = TypeVar("TResolver", bound=AnyResolver)
