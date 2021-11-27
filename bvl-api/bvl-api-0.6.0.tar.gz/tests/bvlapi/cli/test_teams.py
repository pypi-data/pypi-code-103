#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains tests for implementation of teams command.

import unittest.mock as mock

from bvlapi.cli.teams import do_teams
from bvlapi.data.organizations import Organization
from bvlapi.data.teams.team import Team


ORG_DATA_A = {'naam': "BBC Antwerp", "guid": "BVBL1001", "stamNr": "103"}
ORG_DATA_B = {'naam': "BC Bergen", "guid": "BVBL1002", "stamNr": "57"}
ORG_DATA_C = {'naam': "Calodar Zoersel", "guid": "BVBL1003", "stamNr": "71"}

TEAM_J21 = {"naam": "CLUB J21 A", "guid": "BVBL1111J21++1"}
TEAM_J18 = {"naam": "CLUB J18 A", "guid": "BVBL1111J18++1"}
TEAM_J16 = {"naam": "CLUB J16 A", "guid": "BVBL1111J16++1"}


def test__teams__no_search_terms():
    """ Tests that search fails if no search terms are given.
    """
    exit_code, output = do_teams([])
    assert exit_code == 1
    assert output == "unexpected amount of arguments"


def test__teams__too_many_search_terms():
    """ Tests that search fails if too many search terms are given.
    """
    exit_code, output = do_teams(["12", "34"])
    assert exit_code == 1
    assert output == "unexpected amount of arguments"


def test__teams__w_guid_no_teams_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_teams.return_value = []
        exit_code, output = do_teams(["BVBL1002"])

    assert exit_code == 0
    assert output == "no teams were found"


def test__teams__w_guid_one_team_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_teams.return_value = [
            Team(TEAM_J21),
        ]
        exit_code, output = do_teams(["BVBL1002"])

    assert exit_code == 0
    assert output == "CLUB J21 A: BVBL1111J21++1"


def test__teams__w_guid_n_teams_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_teams.return_value = [
            Team(TEAM_J21),
            Team(TEAM_J16),
            Team(TEAM_J18),
        ]
        exit_code, output = do_teams(["BVBL1002"])

    assert exit_code == 0
    assert output == "\n".join([
        "CLUB J21 A: BVBL1111J21++1",
        "CLUB J16 A: BVBL1111J16++1",
        "CLUB J18 A: BVBL1111J18++1",
    ])


def test__teams__w_stam_no_clubs_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_organizations") as mock_get_orgs:
        mock_get_orgs.return_value = []
        exit_code, output = do_teams(["57"])

    assert exit_code == 0
    assert output == "no club with given stamnr found"


def test__teams__w_stam_no_matching_clubs_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_organizations") as mock_get_orgs:
        mock_get_orgs.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        exit_code, output = do_teams(["9999"])

    assert exit_code == 0
    assert output == "no club with given stamnr found"


def test__teams__w_stam_0_teams_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_organizations") as mock_get_orgs, \
         mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_orgs.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        mock_get_teams.return_value = []
        exit_code, output = do_teams(["57"])

    assert exit_code == 0
    assert output == "no teams were found"


def test__teams__w_stam_1_team_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_organizations") as mock_get_orgs, \
         mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_orgs.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        mock_get_teams.return_value = [
            Team(TEAM_J21),
        ]
        exit_code, output = do_teams(["57"])

    assert exit_code == 0
    assert output == "CLUB J21 A: BVBL1111J21++1"


def test__teams__w_stam_n_teams_found():
    """ Tests that correct output is generated if no teams are found.
    """
    with mock.patch("bvlapi.cli.teams.get_organizations") as mock_get_orgs, \
         mock.patch("bvlapi.cli.teams.get_teams") as mock_get_teams:
        mock_get_orgs.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        mock_get_teams.return_value = [
            Team(TEAM_J21),
            Team(TEAM_J16),
            Team(TEAM_J18),
        ]
        exit_code, output = do_teams(["57"])

    assert exit_code == 0
    assert output == "\n".join([
        "CLUB J21 A: BVBL1111J21++1",
        "CLUB J16 A: BVBL1111J16++1",
        "CLUB J18 A: BVBL1111J18++1",
    ])
