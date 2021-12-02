from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="MetadataDefinitionEntry")


@attr.s(auto_attribs=True)
class MetadataDefinitionEntry:
    """ """

    metadata_name: str
    is_editable: bool
    is_multiple: bool
    distinct_metadata_values: List[str]

    def to_dict(self) -> Dict[str, Any]:
        metadata_name = self.metadata_name
        is_editable = self.is_editable
        is_multiple = self.is_multiple
        distinct_metadata_values = self.distinct_metadata_values

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "metadataName": metadata_name,
                "isEditable": is_editable,
                "isMultiple": is_multiple,
                "distinctMetadataValues": distinct_metadata_values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        metadata_name = d.pop("metadataName")

        is_editable = d.pop("isEditable")

        is_multiple = d.pop("isMultiple")

        distinct_metadata_values = cast(List[str], d.pop("distinctMetadataValues"))

        metadata_definition_entry = cls(
            metadata_name=metadata_name,
            is_editable=is_editable,
            is_multiple=is_multiple,
            distinct_metadata_values=distinct_metadata_values,
        )

        return metadata_definition_entry
