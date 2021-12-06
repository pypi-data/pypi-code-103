from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.annotated_doc_annotation_properties import AnnotatedDocAnnotationProperties
from ..models.annotation_term import AnnotationTerm
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotatedDocAnnotation")


@attr.s(auto_attribs=True)
class AnnotatedDocAnnotation:
    """A document annotation"""

    label_name: str
    start: int
    end: int
    text: str
    label_id: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    score: Union[Unset, float] = UNSET
    properties: Union[Unset, AnnotatedDocAnnotationProperties] = UNSET
    terms: Union[Unset, List[AnnotationTerm]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label_name = self.label_name
        start = self.start
        end = self.end
        text = self.text
        label_id = self.label_id
        label = self.label
        score = self.score
        properties: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        terms: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.terms, Unset):
            terms = []
            for terms_item_data in self.terms:
                terms_item = terms_item_data.to_dict()

                terms.append(terms_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "labelName": label_name,
                "start": start,
                "end": end,
                "text": text,
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
        if terms is not UNSET:
            field_dict["terms"] = terms

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_name = d.pop("labelName")

        start = d.pop("start")

        end = d.pop("end")

        text = d.pop("text")

        label_id = d.pop("labelId", UNSET)

        label = d.pop("label", UNSET)

        score = d.pop("score", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, AnnotatedDocAnnotationProperties]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = AnnotatedDocAnnotationProperties.from_dict(_properties)

        terms = []
        _terms = d.pop("terms", UNSET)
        for terms_item_data in _terms or []:
            terms_item = AnnotationTerm.from_dict(terms_item_data)

            terms.append(terms_item)

        annotated_doc_annotation = cls(
            label_name=label_name,
            start=start,
            end=end,
            text=text,
            label_id=label_id,
            label=label,
            score=score,
            properties=properties,
            terms=terms,
        )

        return annotated_doc_annotation
