import pydantic
from typing import List, Optional
from abc import ABC, abstractmethod

import sys

sys.path.insert(1, '/app/models')


# noinspection PyCompatibility
class ReverseGeocodingSchema(pydantic.BaseModel):
    """store data model for reverse geocoding functionality"""
    batch_geocode_count: Optional[int] = 0


class GeneralStrategy(ABC):
    """general strategy, regular"""
    @abstractmethod
    def iter_batch_strategy(self):
        """polymorphism using abstract base class inheritance"""
        pass


class SpreadsheetStrategy(GeneralStrategy):
    """spreadsheet strategy"""
    def iter_batch_strategy(self):
        """simple class init"""
        pass


class SingleStrategy(GeneralStrategy):
    """singular reverse, regular version"""
    def iter_batch_strategy(self):
        """regular init"""
        pass


class BatchStrategy(GeneralStrategy):
    """batch reverse strategy"""
    def iter_batch_strategy(self):
        """batch init"""
        pass
