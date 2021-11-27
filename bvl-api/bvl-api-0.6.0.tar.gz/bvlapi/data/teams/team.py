#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains class used to hold information about a basketball team.

from bvlapi.data.parse import use_fallback_value
from bvlapi.guid.team import is_team_guid


class Team:
    """ Class used to store data about a team retrieved from API.

    :ivar str name: name of team
    :ivar str guid: GUID of team
    """

    def __init__(self, team_data):
        """ Initializes a new instance based on given information.

        :param dict team_data: contains information about team
        """
        self.guid = parse_team_guid(team_data)
        self.name = parse_team_name(team_data)


@use_fallback_value("<UNKNOWN TEAM GUID>")
def parse_team_guid(o):
    """ Used to parse GUID of a team.
    """
    if "guid" not in o:
        return "<MISSING TEAM GUID>"
    value = str(o.get("guid")).replace(" ", "+")
    if not is_team_guid(value):
        return "<INVALID TEAM GUID>"
    return value


@use_fallback_value("<UNKNOWN TEAM NAME>")
def parse_team_name(o):
    """ Used to parse name of a team.
    """
    if "naam" not in o:
        return "<MISSING TEAM NAME>"
    return str(o.get("naam"))
