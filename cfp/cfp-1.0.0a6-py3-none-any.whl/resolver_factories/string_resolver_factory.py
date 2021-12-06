from typing import Optional

from cfp.resolver_factories.resolver_factory import ResolverFactory
from cfp.resolvers import StringResolver
from cfp.sources import AnySource


class StringResolverFactory(ResolverFactory[str, StringResolver]):
    def __init__(self) -> None:
        self._resolver: Optional[StringResolver] = None

    @staticmethod
    def can_resolve(source: AnySource) -> bool:
        return isinstance(source, str)

    def make(self, source: str) -> StringResolver:
        if not self._resolver:
            self._resolver = StringResolver()
        return self._resolver
