from dataclasses import dataclass
from typing import TypeVar, Union


@dataclass
class Source:
    """
    The base configuration of all value resolutions.

    Inherit from this class to describe source configuration for your own
    resolvers.
    """


AnySource = Union[str, Source]
TSource = TypeVar("TSource", bound=AnySource)
