from enum import Enum

from .._base import BaseImportStage


__all__ = 'SOURCE', 'Type', 'ImportStage'

SOURCE = 'DELIVERY_AUTO'


class Type(str, Enum):
    CITY = 'CITY'
    REGION = 'REGION'
    DISTRICT = 'DISTRICT'


ImportStage = BaseImportStage

UKRAINIAN_LANGUAGE = 'uk'
RUSSIAN_LANGUAGE = 'ru'
ENGLISH_LANGUAGE = 'en'

GENERAL_LANGUAGE = UKRAINIAN_LANGUAGE
