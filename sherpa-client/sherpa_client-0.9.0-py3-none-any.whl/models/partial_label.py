from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartialLabel")


@attr.s(auto_attribs=True)
class PartialLabel:
    """ """

    name: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    identifier: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        color = self.color
        identifier = self.identifier

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if label is not UNSET:
            field_dict["label"] = label
        if color is not UNSET:
            field_dict["color"] = color
        if identifier is not UNSET:
            field_dict["identifier"] = identifier

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        label = d.pop("label", UNSET)

        color = d.pop("color", UNSET)

        identifier = d.pop("identifier", UNSET)

        partial_label = cls(
            name=name,
            label=label,
            color=color,
            identifier=identifier,
        )

        return partial_label
