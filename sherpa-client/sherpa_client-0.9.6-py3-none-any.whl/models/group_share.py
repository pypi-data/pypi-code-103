from typing import Any, Dict, Type, TypeVar

import attr

from ..models.share_mode import ShareMode

T = TypeVar("T", bound="GroupShare")


@attr.s(auto_attribs=True)
class GroupShare:
    """ """

    group_name: str
    mode: ShareMode
    can_revoke: bool

    def to_dict(self) -> Dict[str, Any]:
        group_name = self.group_name
        mode = self.mode.to_dict()

        can_revoke = self.can_revoke

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "groupName": group_name,
                "mode": mode,
                "canRevoke": can_revoke,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        group_name = d.pop("groupName")

        mode = ShareMode.from_dict(d.pop("mode"))

        can_revoke = d.pop("canRevoke")

        group_share = cls(
            group_name=group_name,
            mode=mode,
            can_revoke=can_revoke,
        )

        return group_share
