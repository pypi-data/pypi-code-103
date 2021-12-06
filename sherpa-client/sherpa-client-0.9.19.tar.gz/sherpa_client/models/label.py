from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Label")


@attr.s(auto_attribs=True)
class Label:
    """ """

    name: str
    label: str
    color: str
    identifier: Union[Unset, str] = UNSET
    count: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        color = self.color
        identifier = self.identifier
        count = self.count

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "color": color,
            }
        )
        if identifier is not UNSET:
            field_dict["identifier"] = identifier
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        color = d.pop("color")

        identifier = d.pop("identifier", UNSET)

        count = d.pop("count", UNSET)

        label = cls(
            name=name,
            label=label,
            color=color,
            identifier=identifier,
            count=count,
        )

        return label
