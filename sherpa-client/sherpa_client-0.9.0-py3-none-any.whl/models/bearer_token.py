from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="BearerToken")


@attr.s(auto_attribs=True)
class BearerToken:
    """ """

    email: str
    access_token: str

    def to_dict(self) -> Dict[str, Any]:
        email = self.email
        access_token = self.access_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "email": email,
                "access_token": access_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email")

        access_token = d.pop("access_token")

        bearer_token = cls(
            email=email,
            access_token=access_token,
        )

        return bearer_token
