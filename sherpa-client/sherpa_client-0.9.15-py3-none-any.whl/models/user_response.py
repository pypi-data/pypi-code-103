from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserResponse")


@attr.s(auto_attribs=True)
class UserResponse:
    """ """

    username: str
    profilename: str
    permissions: Union[Unset, List[str]] = UNSET
    roles: Union[Unset, List[str]] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    default_group: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        profilename = self.profilename
        permissions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        roles: Union[Unset, List[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        groups: Union[Unset, List[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        default_group = self.default_group
        created_by = self.created_by
        created_at = self.created_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "username": username,
                "profilename": profilename,
            }
        )
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if roles is not UNSET:
            field_dict["roles"] = roles
        if groups is not UNSET:
            field_dict["groups"] = groups
        if default_group is not UNSET:
            field_dict["defaultGroup"] = default_group
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        profilename = d.pop("profilename")

        permissions = cast(List[str], d.pop("permissions", UNSET))

        roles = cast(List[str], d.pop("roles", UNSET))

        groups = cast(List[str], d.pop("groups", UNSET))

        default_group = d.pop("defaultGroup", UNSET)

        created_by = d.pop("createdBy", UNSET)

        created_at = d.pop("createdAt", UNSET)

        user_response = cls(
            username=username,
            profilename=profilename,
            permissions=permissions,
            roles=roles,
            groups=groups,
            default_group=default_group,
            created_by=created_by,
            created_at=created_at,
        )

        return user_response
