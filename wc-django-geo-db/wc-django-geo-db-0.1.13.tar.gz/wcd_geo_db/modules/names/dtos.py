from dataclasses import dataclass

from wcd_geo_db.const import DivisionLevel


__all__ = 'DivisionNameDTO', 'DivisionNameTranslationDTO'


@dataclass
class DivisionNameDTO:
    id: int
    country_id: int
    name: str
    level: DivisionLevel


@dataclass
class DivisionNameTranslationDTO:
    id: int
    language: str
    entity_id: int
    name: str
