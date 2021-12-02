from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartialLexicon")


@attr.s(auto_attribs=True)
class PartialLexicon:
    """ """

    label: str
    name: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label = self.label
        name = self.name
        color = self.color

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "label": label,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label")

        name = d.pop("name", UNSET)

        color = d.pop("color", UNSET)

        partial_lexicon = cls(
            label=label,
            name=name,
            color=color,
        )

        return partial_lexicon
