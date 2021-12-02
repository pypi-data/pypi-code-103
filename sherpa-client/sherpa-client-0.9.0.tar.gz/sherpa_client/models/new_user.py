from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="NewUser")


@attr.s(auto_attribs=True)
class NewUser:
    """ """

    username: str
    password: str
    permissions: List[str]
    roles: List[str]

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        password = self.password
        permissions = self.permissions

        roles = self.roles

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "username": username,
                "password": password,
                "permissions": permissions,
                "roles": roles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        password = d.pop("password")

        permissions = cast(List[str], d.pop("permissions"))

        roles = cast(List[str], d.pop("roles"))

        new_user = cls(
            username=username,
            password=password,
            permissions=permissions,
            roles=roles,
        )

        return new_user
