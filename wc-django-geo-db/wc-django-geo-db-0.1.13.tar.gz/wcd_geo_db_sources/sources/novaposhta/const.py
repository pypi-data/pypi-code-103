from enum import Enum

from .._base import BaseImportStage


__all__ = 'SOURCE', 'Type', 'ImportStage'

SOURCE = 'NOVAPOSHTA'


class Type(str, Enum):
    SETTLEMENT = 'SETTLEMENT'
    CITY = 'CITY'
    AREA = 'AREA'


ImportStage = BaseImportStage

UKRAINIAN_LANGUAGE = 'uk'
RUSSIAN_LANGUAGE = 'ru'
