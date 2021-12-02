from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="LexiconUpdate")


@attr.s(auto_attribs=True)
class LexiconUpdate:
    """ """

    label: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label = self.label
        color = self.color

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label", UNSET)

        color = d.pop("color", UNSET)

        lexicon_update = cls(
            label=label,
            color=color,
        )

        return lexicon_update
