from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Annotator")


@attr.s(auto_attribs=True)
class Annotator:
    """ """

    name: str
    label: str
    engine: str
    favorite: Union[Unset, bool] = UNSET
    is_default: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        engine = self.engine
        favorite = self.favorite
        is_default = self.is_default

        field_dict: Dict[str, Any] = {}
        field_dict.update({"name": name, "label": label, "engine": engine})
        if favorite is not UNSET:
            field_dict["favorite"] = favorite

        if is_default is not UNSET:
            field_dict["isDefault"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        engine = d.pop("engine")

        favorite = d.pop("favorite", UNSET)

        is_default = d.pop("isDefault", UNSET)

        annotator = cls(
            name=name,
            label=label,
            engine=engine,
            favorite=favorite,
            is_default=is_default,
        )

        return annotator
