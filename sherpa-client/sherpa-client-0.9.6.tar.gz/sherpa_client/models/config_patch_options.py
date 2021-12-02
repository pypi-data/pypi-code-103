from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.classification_options import ClassificationOptions
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigPatchOptions")


@attr.s(auto_attribs=True)
class ConfigPatchOptions:
    """ """

    classification: Union[Unset, ClassificationOptions] = UNSET
    label: Union[Unset, str] = UNSET
    metafacets: Union[Unset, List[str]] = UNSET
    image: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        classification: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        label = self.label
        metafacets: Union[Unset, List[str]] = UNSET
        if not isinstance(self.metafacets, Unset):
            metafacets = self.metafacets

        image = self.image

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if classification is not UNSET:
            field_dict["classification"] = classification
        if label is not UNSET:
            field_dict["label"] = label
        if metafacets is not UNSET:
            field_dict["metafacets"] = metafacets
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, ClassificationOptions]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = ClassificationOptions.from_dict(_classification)

        label = d.pop("label", UNSET)

        metafacets = cast(List[str], d.pop("metafacets", UNSET))

        image = d.pop("image", UNSET)

        config_patch_options = cls(
            classification=classification,
            label=label,
            metafacets=metafacets,
            image=image,
        )

        return config_patch_options
