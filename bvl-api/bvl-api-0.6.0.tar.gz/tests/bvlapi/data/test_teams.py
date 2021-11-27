#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains tests for retrieving information about a club's teams.

import pytest
import json

from unittest.mock import patch

from bvlapi.data.teams.team import Team
from bvlapi.data.teams.get import get_teams
from bvlapi.common.exceptions import InvalidGuid

from tests.files import ORG_DETAIL_BY_GUID_JSON


def test_get_teams():
    """ Tests that a list of teams is returned when club is found.
    """
    with patch("bvlapi.data.teams.get.get_detail_by_guid") as call_mock:
        call_mock.return_value = json.loads(ORG_DETAIL_BY_GUID_JSON)
        teams = get_teams("BVBL1004")
        assert len(teams) == 27
        assert teams[3].name == "Antwerp Giants J18 B"
        assert teams[3].guid == "BVBL1004J18++2"


def test_get_teams__invalid_guid():
    """ Tests that an exception is raised when an invalid GUID is provided.
    """
    with pytest.raises(InvalidGuid):
        get_teams("not a valid team GUID")


def test_get_teams__no_club_with_given_guid():
    """ Tests that an empty list is returned when no club is found.
    """
    with patch("bvlapi.data.teams.get.get_detail_by_guid") as call_mock:
        call_mock.return_value = []
        teams = get_teams("BVBL1234")
        assert len(teams) == 0


def test_get_teams__missing_teams_entry():
    """ Tests that an empty list is returned when club has no teams.
    """
    with patch("bvlapi.data.teams.get.get_detail_by_guid") as call_mock:
        call_mock.return_value = [{
                "naam": "Club Zonder Teams",
            }]
        teams = get_teams("BVBL1234")
        assert len(teams) == 0


def test_team__constructor():
    """ Tests constructor of a Team instance.
    """
    team = Team({
        "naam": "Antwerp Giants HSE C",
        "guid": "BVBL1004HSE  3",
    })
    assert team.name == "Antwerp Giants HSE C"
    assert team.guid == "BVBL1004HSE++3"


def test_team__missing_name():
    """ Tests that an appropriate placeholder is used when name is missing.
    """
    team = Team({
        "x": "Antwerp Giants HSE C",
        "guid": "BVBL1004HSE  3",
    })
    assert team.name == "<MISSING TEAM NAME>"
    assert team.guid == "BVBL1004HSE++3"


def test_team__missing_guid():
    """ Tests that an appropriate placeholder is used when team GUID is missing.
    """
    team = Team({
        "naam": "Antwerp Giants HSE C",
        "x": "BVBL1004HSE  3",
    })
    assert team.name == "Antwerp Giants HSE C"
    assert team.guid == "<MISSING TEAM GUID>"


def test_team__invalid_guid():
    """ Tests that an appropriate placeholder is used when team GUID is invalid.
    """
    team = Team({
        "naam": "Antwerp Giants HSE C",
        "guid": "oops",
    })
    assert team.name == "Antwerp Giants HSE C"
    assert team.guid == "<INVALID TEAM GUID>"
