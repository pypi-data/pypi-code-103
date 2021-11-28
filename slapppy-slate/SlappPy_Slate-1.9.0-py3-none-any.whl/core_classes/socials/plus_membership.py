from typing import Optional, Union, List
from uuid import UUID

from slapp_py.core_classes.socials.social import Social

PLUS_BASE_ADDRESS = "sendou.ink/plus/history/"


class PlusMembership(Social):
    def __init__(self,
                 handle: Optional[str] = None,
                 sources: Union[None, UUID, List[UUID]] = None):
        super().__init__(
            value=handle,
            sources=sources,
            social_base_address=PLUS_BASE_ADDRESS
        )

    @property
    def level(self):
        """Returns the Membership's level as an int (or None)"""
        try:
            return int(self.handle.partition('/')[0])
        except ValueError:
            return None

    @property
    def date(self):
        """Returns the Membership's date in form yyyy/M"""
        try:
            return self.handle.partition('/')[2]
        except ValueError:
            return None

    @staticmethod
    def from_dict(obj: dict) -> 'PlusMembership':
        assert isinstance(obj, dict)
        social = Social._from_dict(obj, PLUS_BASE_ADDRESS)
        return PlusMembership(social.handle, social.sources)
