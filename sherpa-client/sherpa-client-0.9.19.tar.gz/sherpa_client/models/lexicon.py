from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Lexicon")


@attr.s(auto_attribs=True)
class Lexicon:
    """ """

    name: str
    label: str
    color: str
    manual_edition_allowed: bool
    terms: Union[Unset, int] = UNSET
    created_by: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    modified_by: Union[Unset, str] = UNSET
    modified_at: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        color = self.color
        manual_edition_allowed = self.manual_edition_allowed
        terms = self.terms
        created_by = self.created_by
        created_at = self.created_at
        modified_by = self.modified_by
        modified_at = self.modified_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "color": color,
                "manualEditionAllowed": manual_edition_allowed,
            }
        )
        if terms is not UNSET:
            field_dict["terms"] = terms
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        color = d.pop("color")

        manual_edition_allowed = d.pop("manualEditionAllowed")

        terms = d.pop("terms", UNSET)

        created_by = d.pop("createdBy", UNSET)

        created_at = d.pop("createdAt", UNSET)

        modified_by = d.pop("modifiedBy", UNSET)

        modified_at = d.pop("modifiedAt", UNSET)

        lexicon = cls(
            name=name,
            label=label,
            color=color,
            manual_edition_allowed=manual_edition_allowed,
            terms=terms,
            created_by=created_by,
            created_at=created_at,
            modified_by=modified_by,
            modified_at=modified_at,
        )

        return lexicon
