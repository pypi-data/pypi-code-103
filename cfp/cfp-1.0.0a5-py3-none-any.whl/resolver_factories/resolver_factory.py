from abc import ABC, abstractmethod
from typing import Any, Generic, cast

from cfp.resolvers.resolver import AnyResolver, TResolver
from cfp.sources import AnySource, TSource


class ResolverFactory(ABC, Generic[TSource, TResolver]):
    """Abstract base resolver factory."""

    @staticmethod
    @abstractmethod
    def can_resolve(source: AnySource) -> bool:
        """
        Returns ``True`` if this factory can manufacture a resolver for
        ``source``.

        Arguments:
            source: Value source

        Returns:
            ``True`` if this factory can manufacture a resolver for ``source``
        """

    @abstractmethod
    def make(self, source: TSource) -> TResolver:
        """
        Makes and returns a resolver for ``source``.

        Arguments:
            source: Value source

        Returns:
            Resolver
        """

    def try_make(self, source: AnySource) -> AnyResolver:
        """
        Makes and returns a resolver for ``source``.

        Arguments:
            source: Value source

        Returns:
            Resolver
        """

        t_source = cast(TSource, source)
        return self.make(source=t_source)


AnyResolverFactory = ResolverFactory[Any, Any]
