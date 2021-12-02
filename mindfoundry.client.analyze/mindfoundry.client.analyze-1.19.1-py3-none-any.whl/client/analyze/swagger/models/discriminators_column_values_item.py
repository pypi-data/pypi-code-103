import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DiscriminatorsColumnValuesItem")

@attr.s(auto_attribs=True)
class DiscriminatorsColumnValuesItem:
    """  """
    column_name: Union[Unset, str] = UNSET
    value: Union[Unset, str, float, int, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        column_name =  self.column_name
        value: Union[Unset, str, float, int, datetime.datetime]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, datetime.datetime):
            value = UNSET
            if not isinstance(self.value, Unset):
                value = self.value.isoformat()

        else:
            value = self.value



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if column_name is not UNSET:
            field_dict["columnName"] = column_name
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        column_name = d.pop("columnName", UNSET)

        def _parse_value(data: Any) -> Union[Unset, str, float, int, datetime.datetime]:
            data = None if isinstance(data, Unset) else data
            value: Union[Unset, str, float, int, datetime.datetime]
            try:
                value = UNSET
                _value = data
                if not isinstance(_value,  Unset):
                    value = isoparse(_value)



                return value
            except: # noqa: E722
                pass
            return cast(Union[Unset, str, float, int, datetime.datetime], data)

        value = _parse_value(d.pop("value", UNSET))


        discriminators_column_values_item = cls(
            column_name=column_name,
            value=value,
        )

        discriminators_column_values_item.additional_properties = d
        return discriminators_column_values_item

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
