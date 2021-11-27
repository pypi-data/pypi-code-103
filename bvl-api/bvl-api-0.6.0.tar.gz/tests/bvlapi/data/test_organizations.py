#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains tests for retrieving information about matches being played by team.

from unittest.mock import patch

from bvlapi.data.organizations.get import get_organizations
from bvlapi.data.organizations.organization import Organization


def test_get_organizations__empty():
    """ Try to retrieve and parse list of organizations returned by API.
    """
    with patch("bvlapi.data.organizations.get.get_list") as call_mock:
        call_mock.return_value = []
        assert len(get_organizations()) == 0


def test_get_organizations__n():
    """ Try to retrieve and parse list of organizations returned by API.
    """
    with patch("bvlapi.data.organizations.get.get_list") as call_mock:
        call_mock.return_value = [{
            "naam": "Antwerp Giants",
            "guid": "BVBL1004",
            "stamNr": "71",
        }, {
            "naam": "BC Machelen-Diegem",
            "guid": "BVBL1005",
            "stamNr": "76",
        }]
        assert len(get_organizations()) == 2


def test_organization__constructor():
    """ Try to create a new instance of Organization.
    """
    org = Organization({
        "naam": "Antwerp Giants",
        "guid": "BVBL1004",
        "stamNr": "71",
    })
    assert org.name == "Antwerp Giants"
    assert org.guid == "BVBL1004"


def test_organization__missing_naam():
    """ Try to create new instance of Organization, but 'naam' entry is
        missing from dictionary.
    """
    org = Organization({
            "x": "Antwerp Giants",
            "guid": "BVBL1004",
            "stamNr": "71",
        })
    assert org.name == "<UNKNOWN CLUB NAME>"
    assert org.guid == "BVBL1004"
    assert org.stam == "71"


def test_organization__missing_guid():
    """ Try to create new instance of Organization, but 'guid' entry is
        missing from dictionary.
    """
    org = Organization({
            "naam": "Antwerp Giants",
            "x": "BVBL1004",
            "stamNr": "71",
        })
    assert org.name == "Antwerp Giants"
    assert org.guid == "<UNKNOWN CLUB GUID>"
    assert org.stam == "71"


def test_organization__invalid_guid():
    """ Try to create new instance of Organization, but 'guid' entry contains
        an invalid GUID value.
    """
    org = Organization({
            "naam": "Antwerp Giants",
            "guid": "x",
            "stamNr": "71",
        })
    assert org.name == "Antwerp Giants"
    assert org.guid == "<INVALID CLUB GUID>"
    assert org.stam == "71"


def test_organization__missing_stamnr():
    """ Try to create new instance of Organization, but 'stam' entry is
        missing from dictionary.
    """
    org = Organization({
        "naam": "Antwerp Giants",
        "guid": "BVBL1004",
        "x": "71",
    })
    assert org.name == "Antwerp Giants"
    assert org.guid == "BVBL1004"
    assert org.stam == "<UNKNOWN STAM NR>"
