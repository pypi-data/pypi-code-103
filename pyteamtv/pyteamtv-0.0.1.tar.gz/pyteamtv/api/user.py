import jwt

from pyteamtv.infra.requester import Requester
from pyteamtv.models.list import List
from pyteamtv.models.membership import Membership
from pyteamtv.models.membership_list import MembershipList
from pyteamtv.models.sharing_group import SharingGroup

from .endpoint import API_ENDPOINT
from .token import TOKEN
from ..models.resource_group.team import TeamResourceGroup


class TeamTVUser(object):
    def __init__(self, jwt_token):
        token = jwt.decode(
            jwt_token,
            TOKEN,
            algorithms='RS256',
            verify=False,
            options={
                'verify_signature': False
            }
        )

        self._requester = Requester(
            f"{API_ENDPOINT}/api",
            jwt_token
        )
        self.__token = token

    def get_membership_list(self):
        """
        :return: MembershipList
        """
        return MembershipList(
            Membership,
            self._requester,
            "GET",
            "/users/me/memberships"
        )

    def get_public_sharing_groups(self):
        return List(
            SharingGroup,
            self._requester,
            "GET",
            "/sharingGroups"
        )

    def get_team(self, name: str) -> TeamResourceGroup:
        membership_list = self.get_membership_list()
        resource_group = membership_list.get_membership_by_name(
            name=name
        ).resource_group  # type: TeamResourceGroup
        return resource_group
