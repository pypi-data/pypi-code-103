from __future__ import annotations

from enum import Enum
from typing import Callable, Optional, TypeVar, Dict

from pydantic import Field
from pydantic.dataclasses import dataclass

from mr_scraper.api.transforms import get_attribute, get_text

Input = TypeVar("Input")
Value = TypeVar("Value")

TransformFunction = Callable[[Input], Value]
GetUrl = Callable[[Dict[str, any]], str]


class ContentProvider(Enum):
    REQUEST = 1
    PUPPETEER = 2


@dataclass
class QueryConfig:
    selector: str
    transform: Optional[TransformFunction] = lambda x: x
    queries: Optional[Dict[str, QueryConfig]] = None


QueryConfig.__pydantic_model__.update_forward_refs()


@dataclass
class ContentConfig:
    provider: ContentProvider
    delay: int = Field(default=2, description="delay before get content")
    url: GetUrl = lambda x: x.get('url')
    transform: Optional[TransformFunction] = None


@dataclass
class ScraperConfig:
    content: ContentConfig
    queries: Dict[str, QueryConfig]


def base_url(base: str) -> GetUrl:
    def wrapper(payload: dict):
        return f'{base}{payload["url"]}'

    return wrapper


def compose_transform(function, fields: Dict[str, any]):
    fn = fields.get('transform', lambda x: x)
    return lambda x: fn(function(x))


def default_query_fields(selector: str, **kwargs):
    fields = dict(**kwargs)
    fields['selector'] = selector
    return fields


def query_config(*attrs: str):
    """
    decorate a function that return a dictionary with the parameters of the QueryConfig
    :param attrs: custom attributes
    :return:
    """

    def decorator(function):
        def wrapper(selector: str, **kwargs) -> QueryConfig:
            fields = default_query_fields(selector, **kwargs)
            args = {'fields': fields}
            for v in attrs:
                args[v] = fields.get(v)
            fields = function(**args)
            return QueryConfig(
                selector=fields.get('selector'),
                transform=fields.get('transform'),
                queries=fields.get('queries')
            )

        return wrapper

    return decorator


@query_config('attribute')
def attribute_query(attribute: str, fields: dict):
    fields['transform'] = compose_transform(lambda x: get_attribute(x, attribute), fields)
    return fields


@query_config()
def text_query(fields: dict):
    fields['transform'] = compose_transform(get_text, fields)
    return fields
