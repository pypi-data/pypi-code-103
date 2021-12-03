from typing import Any, Optional, Sequence, Tuple
from wcd_geo_db.modules.client import DBClientMixin
from px_client_builder import NestedClient
from wcd_geo_db.const import DivisionLevel

from ..dtos import DivisionNameDTO, DivisionNameTranslationDTO


__all__ = 'DivisionsClient',

CodeSeekDefinition = Tuple[str, Any]


class DivisionsClient(DBClientMixin, NestedClient):
    # model: Type[Division] = Division
    # _qs: DivisionsQuerySet

    def get(self, country_id: int, levels: Optional[Sequence[DivisionLevel]] = None) -> Sequence[DivisionNameDTO]:
        return []

    def get_translations(
        self,
        ids: Sequence[int],
        language: str,
        fallback_languages: Sequence[str] = []
    ) -> Sequence[DivisionNameTranslationDTO]:
        return []

    def find(
        self,
        ids: Optional[Sequence[int]] = None,
        levels: Optional[Sequence[DivisionLevel]] = None,
        search_query: Optional[str] = None,
        **kw
    ) -> Sequence[int]:
        """Searches for an entities."""

        return []
