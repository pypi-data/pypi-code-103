from typing import Optional, TypeVar, TypedDict

from .base import QuerySet


__all__ = 'SearchQueryParam', 'SearchQuerySet',

QT = TypeVar('QT', bound='SearchQuerySet')


class SearchQueryParam(TypedDict):
    language: str
    query: str
    min_rank: Optional[float]
    use_simple_search: Optional[bool]


class SearchQuerySet(QuerySet):
    def search(self: QT, query: SearchQueryParam) -> QT:
        return self

    def general_filter(
        self: QT,
        search_query: Optional[SearchQueryParam] = None,
        **kw
    ) -> QT:
        q = super().general_filter(**kw)

        if search_query is not None and search_query.get('query'):
            return q.search(query=search_query)

        return q
