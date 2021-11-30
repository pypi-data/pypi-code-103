from types import MappingProxyType
from typing import Dict, Mapping, NamedTuple, Optional, Sequence, Tuple, Union

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.elements import ClauseElement, Label

from .typing import OrderByType

__all__ = [
    'SearchParams',
    'Search',
    'GroupByRelationship',
    'GroupBy',
    'PagingParams',
    'Paging',
]


class SearchParams(NamedTuple):
    search: Dict[str, Union[str, Dict[str, str]]] = {}
    and_joint: Optional[bool] = None
    search_type: Dict[str, Union[int, Dict[str, int]]] = {}


class Search(NamedTuple):
    params: SearchParams
    filters: Tuple[ClauseElement, ...] = ()


class GroupByRelationship(NamedTuple):
    key: str
    sa_cls: DeclarativeMeta


class GroupBy(NamedTuple):
    params: Tuple[str, ...] = ()
    columns: Tuple[Label, ...] = ()
    relationship_map: Mapping[str, GroupByRelationship] = MappingProxyType({})


class PagingParams(NamedTuple):
    page: int
    start: int
    limit: Optional[int]
    asc: Sequence[bool]
    sort_by: Optional[Sequence[str]]


class Paging(NamedTuple):
    start: int
    stop: Optional[int]
    order_by: Tuple[OrderByType, ...]
