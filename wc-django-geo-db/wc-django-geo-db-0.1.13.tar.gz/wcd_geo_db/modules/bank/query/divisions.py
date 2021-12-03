from typing import Any, List, Optional, Sequence, TypeVar
from django.db import models
from django.db.models.fields import BooleanField, IntegerField
from django.db.models.functions import Cast
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest

from wcd_geo_db.const import DivisionLevel
from wcd_geo_db.modules.code_seeker.query import CodeSeekerQuerySet
from pxd_tree.hierarchy import TreeQuerySet

from ..dtos import DivisionDTO, GeometryDTO
from .base import QuerySet
from .geometry import WithGeometryQuerySet
from .search import SearchQueryParam, SearchQuerySet


__all__ = 'DivisionsQuerySet',

QT = TypeVar('QT', bound='DivisionsQuerySet')
VALUES_NAMES = (
    'id', 'name', 'level', 'types', 'codes', 'parent_id', 'path',
    'geometry__location', 'geometry__polygon',
)


def as_dto(values: dict) -> DivisionDTO:
    return DivisionDTO(
        id=values['id'],
        name=values['name'],
        level=DivisionLevel(values['level']),
        types=values['types'],
        codes=values['codes'],
        parent_id=values['parent_id'],
        path=list(values['path']),
        geometry=GeometryDTO(
            location=values['geometry__location'],
            polygon=values['geometry__polygon'],
        )
    )


class DivisionsQuerySet(
    WithGeometryQuerySet,
    CodeSeekerQuerySet,
    TreeQuerySet,
    SearchQuerySet,
    QuerySet
):
    SEARCH_QUERY_MIN_LENGTH: int = 1
    SEARCH_QUERY_MIN_RANK: float = 0.1
    SEARCH_QUERY_RANK_WEIGHTS: Sequence[float] = [0.2, 0.4, 0.8, 1]

    def _search_rank_order(self: QT, query: SearchQueryParam) -> QT:
        q = query.get('query')
        min_rank = query.get('min_rank', self.SEARCH_QUERY_MIN_RANK)

        name_equality = models.Case(
            models.When(name__iexact=q, then=models.Value(1)),
            models.When(translations__name__iexact=q, then=models.Value(1)),
            default=models.Value(0),
            output_field=models.IntegerField()
        )
        name_similarity = Greatest(
            TrigramSimilarity(
                'name', Cast(models.Value(q), output_field=models.TextField()),
                function='strict_word_similarity'
            ),
            TrigramSimilarity(
                'translations__name', Cast(models.Value(q), output_field=models.TextField()),
                function='strict_word_similarity'
            ),
        )
        synonyms_similarity = Greatest(
            TrigramSimilarity(
                'synonyms', Cast(models.Value(q), output_field=models.TextField()),
                function='strict_word_similarity'
            ),
            TrigramSimilarity(
                'translations__synonyms', Cast(models.Value(q), output_field=models.TextField()),
                function='strict_word_similarity'
            ),
        )

        queryset = (
            self
            .annotate(
                name_equality=name_equality,
                name_similarity=name_similarity,
                synonyms_similarity=synonyms_similarity,
            )
            .filter(
                models.Q(name_equality=1)
                |
                models.Q(name_similarity__gt=min_rank)
                |
                models.Q(synonyms_similarity__gt=min_rank)
            )
            .order_by('-name_equality', '-name_similarity', '-synonyms_similarity')
        )

        return queryset

    def _search_simple_similarity(self: QT, query: SearchQueryParam) -> QT:
        q = query.get('query')

        name_equality = models.Case(
            models.When(name__iexact=q, then=models.Value(1)),
            models.When(translations__name__iexact=q, then=models.Value(1)),
            default=models.Value(0),
            output_field=models.IntegerField()
        )

        queryset = (
            self
            .annotate(name_equality=name_equality)
            .filter(
                models.Q(name_equality=1)
                |
                models.Q(name__icontains=q)
                |
                models.Q(translations__name__icontains=q)
            )
            .order_by('-name_equality')
        )

        return queryset

    def search(self: QT, query: SearchQueryParam) -> QT:
        q = query.get('query')

        if not q or len(q) < self.SEARCH_QUERY_MIN_LENGTH:
            return self

        if query.get('use_simple_search'):
            return self._search_simple_similarity(query)

        return self._search_rank_order(query)


    def as_dtos(self) -> List[DivisionDTO]:
        return [as_dto(values) for values in self.values(*VALUES_NAMES)]

    def general_filter(
        self: QT,
        parent_ids: Optional[Sequence[int]] = None,
        levels: Optional[Sequence[DivisionLevel]] = None,
        types: Optional[Sequence[str]] = None,
        **kw
    ) -> QT:
        q = (
            super().general_filter(**kw)
            .optional_in('parent_id', parent_ids)
            .optional_in('level', levels)
            .optional_overlap('types', types)
        )

        return q
