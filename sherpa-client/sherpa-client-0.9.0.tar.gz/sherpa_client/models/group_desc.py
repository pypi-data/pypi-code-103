from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupDesc")


@attr.s(auto_attribs=True)
class GroupDesc:
    """ """

    name: str
    label: str
    max_users: int
    created_by: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    modified_by: Union[Unset, str] = UNSET
    modified_at: Union[Unset, str] = UNSET
    attached_roles: Union[Unset, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        max_users = self.max_users
        created_by = self.created_by
        created_at = self.created_at
        modified_by = self.modified_by
        modified_at = self.modified_at
        attached_roles: Union[Unset, List[str]] = UNSET
        if not isinstance(self.attached_roles, Unset):
            attached_roles = self.attached_roles

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "maxUsers": max_users,
            }
        )
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if attached_roles is not UNSET:
            field_dict["attachedRoles"] = attached_roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        max_users = d.pop("maxUsers")

        created_by = d.pop("createdBy", UNSET)

        created_at = d.pop("createdAt", UNSET)

        modified_by = d.pop("modifiedBy", UNSET)

        modified_at = d.pop("modifiedAt", UNSET)

        attached_roles = cast(List[str], d.pop("attachedRoles", UNSET))

        group_desc = cls(
            name=name,
            label=label,
            max_users=max_users,
            created_by=created_by,
            created_at=created_at,
            modified_by=modified_by,
            modified_at=modified_at,
            attached_roles=attached_roles,
        )

        return group_desc
