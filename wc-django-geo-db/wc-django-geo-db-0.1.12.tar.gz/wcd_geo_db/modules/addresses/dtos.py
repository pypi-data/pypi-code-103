from dataclasses import dataclass
from typing import Optional, Sequence, Union
from typing_extensions import TypedDict

from ..bank.dtos import DivisionDTO


__all__ = 'AddressDefinitionDTO', 'FormattedAddressDTO',


class AddressDefinitionDTO(TypedDict):
    divisions_path: Optional[Sequence[
        Union[int, DivisionDTO]
    ]]
    division: Optional[Union[int, DivisionDTO]]


@dataclass
class FormattedAddressDTO:
    id: str
    divisions: Sequence[DivisionDTO]
    formatted_address: str
