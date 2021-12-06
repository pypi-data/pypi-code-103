from typing import Dict, Optional

from cfp.resolver_factories.resolver_factory import ResolverFactory
from cfp.resolvers import ParameterStoreResolver
from cfp.sources import AnySource, FromParameterStore
from cfp.types import RegionName


class ParameterStoreResolverFactory(
    ResolverFactory[
        FromParameterStore,
        ParameterStoreResolver,
    ]
):
    def __init__(self) -> None:
        self._resolvers: Dict[Optional[RegionName], ParameterStoreResolver] = {}

    @staticmethod
    def can_resolve(source: AnySource) -> bool:
        return isinstance(source, FromParameterStore)

    def make(self, source: FromParameterStore) -> ParameterStoreResolver:
        if existing := self._resolvers.get(source.region, None):
            return existing

        resolver = ParameterStoreResolver()
        self._resolvers[source.region] = resolver
        return resolver
