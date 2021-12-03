from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="DeleteGroupResult")


@attr.s(auto_attribs=True)
class DeleteGroupResult:
    """ """

    removed_users: int
    removed_projects: int

    def to_dict(self) -> Dict[str, Any]:
        removed_users = self.removed_users
        removed_projects = self.removed_projects

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "removedUsers": removed_users,
                "removedProjects": removed_projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        removed_users = d.pop("removedUsers")

        removed_projects = d.pop("removedProjects")

        delete_group_result = cls(
            removed_users=removed_users,
            removed_projects=removed_projects,
        )

        return delete_group_result
