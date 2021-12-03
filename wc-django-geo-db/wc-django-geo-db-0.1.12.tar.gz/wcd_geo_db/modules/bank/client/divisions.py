from typing import Any, List, Optional, Sequence, Tuple, Type
from wcd_geo_db.modules.bank.db.translations import DivisionTranslation
from wcd_geo_db.modules.client import CodeSeekingClientMixin, DBClientMixin
from px_client_builder import NestedClient
from wcd_geo_db.const import DivisionLevel
from wcd_geo_db.modules.code_seeker.query import CodeSeekSeq
from wcd_geo_db.utils import response_with_ordering

from ..query.geometry import Area
from ..dtos import DivisionDTO, DivisionTranslationDTO
from ..db import Division
from ..query import DivisionsQuerySet, SearchQueryParam


__all__ = 'DivisionsClient',

CodeSeekDefinition = Tuple[str, Any]


class DivisionsClient(DBClientMixin, CodeSeekingClientMixin, NestedClient):
    model: Type[Division] = Division
    _qs: DivisionsQuerySet

    def get(self, ids: Sequence[int], keep_ordering: bool = False) -> Sequence[DivisionDTO]:
        if keep_ordering:
            ids = list(ids)

        response = self._qs.general_filter(ids=ids).as_dtos()

        if keep_ordering:
            response = response_with_ordering(ids, response)

        return response

    def get_by_code(self, code: str, value: Any) -> Sequence[DivisionDTO]:
        return self.get(self.find(self._qs, codes=((code, value),)))

    def get_translations(
        self,
        ids: Sequence[int],
        language: str,
        fallback_languages: Sequence[str] = []
    ) -> Sequence[DivisionDTO]:
        query = DivisionTranslation.objects.filter(entity_id__in=ids)

        if fallback_languages:
            query = query.by_language_order(*[language] + fallback_languages)
        else:
            query = query.by_language(language)

        return [
            DivisionTranslationDTO(
                id=e.id,
                language=e.language,
                entity_id=e.entity_id,
                name=e.name
            )
            for e in query
        ]

    def find(
        self,
        ids: Optional[Sequence[int]] = None,
        parent_ids: Optional[Sequence[int]] = None,
        levels: Optional[Sequence[DivisionLevel]] = None,
        codes: Optional[Sequence[Tuple[str, Any]]] = None,
        types: Optional[Sequence[str]] = None,
        location_areas: Optional[Sequence[Area]] = None,
        search_query: Optional[SearchQueryParam] = None,
        **kw
    ) -> Sequence[int]:
        """Searches for an entities."""

        return (
            self._qs
            .general_filter(
                ids=ids,
                parent_ids=parent_ids,
                levels=levels,
                types=types,
                codes_filter=self._get_codes_filter(codes),
                location_areas=location_areas,
                search_query=search_query,
                **kw
            )
            .ids()
        )

    def find_descendants(
        self,
        ids: Sequence[int],
        levels: Optional[Sequence[DivisionLevel]] = None,
        codes: Optional[Sequence[Tuple[str, Any]]] = None,
        types: Optional[Sequence[str]] = None,
        location_areas: Optional[Sequence[Area]] = None,
        search_query: Optional[SearchQueryParam] = None,
        **kw
    ) -> Sequence[int]:
        """Searches for a descendants of objects from `ids`."""

        return (
            self._qs
            .general_filter(ids=ids)
            .descendants(within=self._qs.general_filter(
                levels=levels,
                codes_filter=self._get_codes_filter(codes),
                types=types,
                location_areas=location_areas,
                search_query=search_query,
                **kw
            ))
            .ids()
        )

    def find_ancestors(
        self,
        ids: Sequence[int],
        levels: Optional[Sequence[DivisionLevel]] = None,
        codes: Optional[Sequence[Tuple[str, Any]]] = None,
        types: Optional[Sequence[str]] = None,
        location_areas: Optional[Sequence[Area]] = None,
        search_query: Optional[SearchQueryParam] = None,
        **kw
    ) -> Sequence[int]:
        """Searches for an ancestors of objects from `ids`."""

        return (
            self._qs
            .general_filter(ids=ids)
            .ancestors(within=self._qs.general_filter(
                levels=levels,
                codes_filter=self._get_codes_filter(codes),
                types=types,
                location_areas=location_areas,
                search_query=search_query,
                **kw
            ))
            .ids()
        )
