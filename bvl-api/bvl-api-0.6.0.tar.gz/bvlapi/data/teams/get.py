#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains functionality to retrieve a list of team's for a given club.

from bvlapi.api.org.detail_by_guid import get_detail_by_guid
from bvlapi.common.exceptions import InvalidGuid
from bvlapi.data.teams.team import Team
from bvlapi.guid.club import is_club_guid


def get_teams(club_guid):
    """ Returns a list of club's teams.

    :param str club_guid: GUID of team

    :rtype: []
    :return: a list of objects containing information about a club's teams
    """
    if not is_club_guid(club_guid):
        raise InvalidGuid("expected a valid club GUID")

    search_results = get_detail_by_guid(club_guid)
    if len(search_results) == 0:
        return []

    club_information = search_results[0]
    if "teams" not in club_information:
        return []

    return [Team(team_info) for team_info in club_information["teams"]]
