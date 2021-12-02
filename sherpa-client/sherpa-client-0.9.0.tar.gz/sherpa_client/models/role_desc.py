from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoleDesc")


@attr.s(auto_attribs=True)
class RoleDesc:
    """ """

    rolename: str
    label: str
    permissions: List[str]
    type: str
    group_name: Union[Unset, str] = UNSET
    predefined: Union[Unset, bool] = UNSET
    created_at: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    modified_by: Union[Unset, str] = UNSET
    modified_at: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        rolename = self.rolename
        label = self.label
        permissions = self.permissions

        type = self.type
        group_name = self.group_name
        predefined = self.predefined
        created_at = self.created_at
        created_by = self.created_by
        modified_by = self.modified_by
        modified_at = self.modified_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "rolename": rolename,
                "label": label,
                "permissions": permissions,
                "type": type,
            }
        )
        if group_name is not UNSET:
            field_dict["groupName"] = group_name
        if predefined is not UNSET:
            field_dict["predefined"] = predefined
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        rolename = d.pop("rolename")

        label = d.pop("label")

        permissions = cast(List[str], d.pop("permissions"))

        type = d.pop("type")

        group_name = d.pop("groupName", UNSET)

        predefined = d.pop("predefined", UNSET)

        created_at = d.pop("createdAt", UNSET)

        created_by = d.pop("createdBy", UNSET)

        modified_by = d.pop("modifiedBy", UNSET)

        modified_at = d.pop("modifiedAt", UNSET)

        role_desc = cls(
            rolename=rolename,
            label=label,
            permissions=permissions,
            type=type,
            group_name=group_name,
            predefined=predefined,
            created_at=created_at,
            created_by=created_by,
            modified_by=modified_by,
            modified_at=modified_at,
        )

        return role_desc
