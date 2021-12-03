from decimal import Decimal
from typing import Any, List, Optional, Tuple, TypedDict

from wcd_geo_db.const import DivisionLevel, DivisionType


__all__ = 'CodesItem', 'DivisionItem', 'DivisionTranslationItem',


class CodesItem(TypedDict):
    code: Tuple[str, Any]
    codes: List[Tuple[str, Any]]


class Point(TypedDict):
    latitude: Decimal
    longitude: Decimal


class DivisionItem(CodesItem, TypedDict):
    path: List[Tuple[str, Any]]
    name: Optional[str]
    types: List[DivisionType]
    level: DivisionLevel
    point: Optional[Point]


class DivisionTranslationItem(TypedDict):
    language: Optional[str]
    code: Tuple[str, Any]
    name: Optional[str]
    synonyms: Optional[str]
