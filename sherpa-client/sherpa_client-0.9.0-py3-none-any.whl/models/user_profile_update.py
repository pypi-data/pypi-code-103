from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserProfileUpdate")


@attr.s(auto_attribs=True)
class UserProfileUpdate:
    """ """

    profilename: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        profilename = self.profilename
        password = self.password

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if profilename is not UNSET:
            field_dict["profilename"] = profilename
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        profilename = d.pop("profilename", UNSET)

        password = d.pop("password", UNSET)

        user_profile_update = cls(
            profilename=profilename,
            password=password,
        )

        return user_profile_update
