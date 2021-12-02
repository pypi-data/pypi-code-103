from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupPatch")


@attr.s(auto_attribs=True)
class GroupPatch:
    """ """

    label: Union[Unset, str] = UNSET
    max_users: Union[Unset, int] = UNSET
    attached_roles: Union[Unset, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label = self.label
        max_users = self.max_users
        attached_roles: Union[Unset, List[str]] = UNSET
        if not isinstance(self.attached_roles, Unset):
            attached_roles = self.attached_roles

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if max_users is not UNSET:
            field_dict["maxUsers"] = max_users
        if attached_roles is not UNSET:
            field_dict["attachedRoles"] = attached_roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label", UNSET)

        max_users = d.pop("maxUsers", UNSET)

        attached_roles = cast(List[str], d.pop("attachedRoles", UNSET))

        group_patch = cls(
            label=label,
            max_users=max_users,
            attached_roles=attached_roles,
        )

        return group_patch
