from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import DataClassJsonMixin


class UnitDTO(str, Enum):
    DATE = 'date'
    NUMBER = 'number'
    TEXT = 'text'
    BOOLEAN = 'boolean'


@dataclass
class HeaderDescriptionDTO(DataClassJsonMixin):
    id: str
    unit: UnitDTO


@dataclass
class TableDTO(DataClassJsonMixin):
    headers: List[HeaderDescriptionDTO]
    values: List[list]
