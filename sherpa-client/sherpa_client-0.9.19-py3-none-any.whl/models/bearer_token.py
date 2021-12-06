from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="BearerToken")


@attr.s(auto_attribs=True)
class BearerToken:
    """ """

    username: str
    profilename: str
    access_token: str

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        profilename = self.profilename
        access_token = self.access_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "username": username,
                "profilename": profilename,
                "access_token": access_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")
        profilename = d.pop("profilename")
        access_token = d.pop("access_token")

        bearer_token = cls(
            username=username,
            profilename=profilename,
            access_token=access_token,
        )

        return bearer_token
