from dataclasses import dataclass
from typing import List, Optional, Sequence
from django.contrib.gis.geos import Point, Polygon

from wcd_geo_db.const import DivisionLevel


__all__ = 'GeometryDTO', 'DivisionDTO', 'DivisionTranslationDTO'


@dataclass
class GeometryDTO:
    location: Optional[Point]
    polygon: Optional[Polygon]


@dataclass
class DivisionDTO:
    id: int
    name: str
    level: DivisionLevel
    types: List[str]
    codes: dict
    parent_id: int
    path: Sequence[int]
    geometry: GeometryDTO


@dataclass
class DivisionTranslationDTO:
    id: int
    language: str
    entity_id: int
    name: str
