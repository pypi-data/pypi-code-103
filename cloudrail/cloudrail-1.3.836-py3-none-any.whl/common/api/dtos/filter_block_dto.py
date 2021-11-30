from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class OptionalFilterFieldDTO(DataClassJsonMixin):
    id: str
    name: str


@dataclass
class FilterBlockDTO(DataClassJsonMixin):
    id: str
    name: str
    optional_fields: List[OptionalFilterFieldDTO]
    empty_text: Optional[str] = None
