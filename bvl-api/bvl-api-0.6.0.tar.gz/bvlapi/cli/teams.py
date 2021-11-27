#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains functionality implementing the `teams` command.

from bvlapi.data.teams.get import get_teams
from bvlapi.data.organizations.get import get_organizations
from bvlapi.guid.club import is_club_guid


def do_teams(search_terms):
    """ Gives a list of information about a club's teams.

    :param List[str] search_terms: a list of search terms

    :return: exit code and output
    :rtype: Tuple[int, str]
    """
    if len(search_terms) != 1:
        return 1, "unexpected amount of arguments"
    club_id = search_terms[0]
    if is_club_guid(club_id):
        return _do_teams_w_guid(club_id)
    else:
        return _do_teams_w_stam(club_id)


def _do_teams_w_guid(guid):
    """ Lists teams of club with a given GUID.

    :param str guid: GUID of club

    :return: exit code and output
    :rtype: Tuple[int, str]
    """
    teams = get_teams(guid)
    if not teams:
        return 0, "no teams were found"
    lines = []
    for team in teams:
        lines.append(team.name + ": " + team.guid)
    return 0, "\n".join(lines)


def _do_teams_w_stam(stam):
    """ Lists teams of club with a given stamnr.

    :param str stamnr: stamnr of club

    :return: exit code and output
    :rtype: Tuple[int, str]
    """
    clubs = get_organizations()
    for club in clubs:
        if club.stam == stam:
            return _do_teams_w_guid(club.guid)
    return 0, "no club with given stamnr found"
