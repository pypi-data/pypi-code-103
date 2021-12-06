from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.annotated_doc_category_properties import AnnotatedDocCategoryProperties
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotatedDocCategory")


@attr.s(auto_attribs=True)
class AnnotatedDocCategory:
    """A document category"""

    label_name: str
    label_id: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    score: Union[Unset, float] = UNSET
    properties: Union[Unset, AnnotatedDocCategoryProperties] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label_name = self.label_name
        label_id = self.label_id
        label = self.label
        score = self.score
        properties: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "labelName": label_name,
            }
        )
        if label_id is not UNSET:
            field_dict["labelId"] = label_id
        if label is not UNSET:
            field_dict["label"] = label
        if score is not UNSET:
            field_dict["score"] = score
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_name = d.pop("labelName")

        label_id = d.pop("labelId", UNSET)

        label = d.pop("label", UNSET)

        score = d.pop("score", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, AnnotatedDocCategoryProperties]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = AnnotatedDocCategoryProperties.from_dict(_properties)

        annotated_doc_category = cls(
            label_name=label_name,
            label_id=label_id,
            label=label,
            score=score,
            properties=properties,
        )

        return annotated_doc_category
