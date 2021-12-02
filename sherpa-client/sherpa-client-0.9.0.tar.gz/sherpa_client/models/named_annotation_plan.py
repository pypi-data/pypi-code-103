from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.annotation_plan import AnnotationPlan
from ..types import UNSET, Unset

T = TypeVar("T", bound="NamedAnnotationPlan")


@attr.s(auto_attribs=True)
class NamedAnnotationPlan:
    """ """

    name: str
    label: str
    parameters: AnnotationPlan
    created_at: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    modified_by: Union[Unset, str] = UNSET
    modified_at: Union[Unset, str] = UNSET
    favorite: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        parameters = self.parameters.to_dict()

        created_at = self.created_at
        created_by = self.created_by
        modified_by = self.modified_by
        modified_at = self.modified_at
        favorite = self.favorite

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "parameters": parameters,
            }
        )
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if favorite is not UNSET:
            field_dict["favorite"] = favorite

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        parameters = AnnotationPlan.from_dict(d.pop("parameters"))

        created_at = d.pop("createdAt", UNSET)

        created_by = d.pop("createdBy", UNSET)

        modified_by = d.pop("modifiedBy", UNSET)

        modified_at = d.pop("modifiedAt", UNSET)

        favorite = d.pop("favorite", UNSET)

        named_annotation_plan = cls(
            name=name,
            label=label,
            parameters=parameters,
            created_at=created_at,
            created_by=created_by,
            modified_by=modified_by,
            modified_at=modified_at,
            favorite=favorite,
        )

        return named_annotation_plan
