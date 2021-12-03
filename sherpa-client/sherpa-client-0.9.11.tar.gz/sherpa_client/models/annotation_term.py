from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.annotation_term_properties import AnnotationTermProperties
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotationTerm")


@attr.s(auto_attribs=True)
class AnnotationTerm:
    """A term"""

    identifier: str
    lexicon: str
    preferred_form: Union[Unset, str] = UNSET
    score: Union[Unset, int] = UNSET
    properties: Union[Unset, AnnotationTermProperties] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        lexicon = self.lexicon
        preferred_form = self.preferred_form
        score = self.score
        properties: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
                "lexicon": lexicon,
            }
        )
        if preferred_form is not UNSET:
            field_dict["preferredForm"] = preferred_form
        if score is not UNSET:
            field_dict["score"] = score
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        lexicon = d.pop("lexicon")

        preferred_form = d.pop("preferredForm", UNSET)

        score = d.pop("score", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, AnnotationTermProperties]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = AnnotationTermProperties.from_dict(_properties)

        annotation_term = cls(
            identifier=identifier,
            lexicon=lexicon,
            preferred_form=preferred_form,
            score=score,
            properties=properties,
        )

        return annotation_term
