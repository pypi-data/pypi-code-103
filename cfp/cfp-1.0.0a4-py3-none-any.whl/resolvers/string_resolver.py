from typing import Dict, Iterator

from cfp.resolvers.resolver import Resolver
from cfp.types import ApiParameter, StackParameterKey


class StringResolver(Resolver[str]):
    def __init__(self) -> None:
        self._values: Dict[StackParameterKey, str] = {}

    def _queue(self, key: StackParameterKey, source: str) -> None:
        self._values[key] = source

    def resolve(self) -> Iterator[ApiParameter]:
        for v in self._values:
            yield ApiParameter(
                ParameterKey=v,
                ParameterValue=self._values[v],
            )
