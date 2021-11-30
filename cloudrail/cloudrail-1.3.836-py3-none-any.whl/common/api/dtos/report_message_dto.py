from dataclasses import dataclass
from typing import List

from dataclasses_json import DataClassJsonMixin


@dataclass
class ReportMessageDTO(DataClassJsonMixin):
    messages: List[str]
