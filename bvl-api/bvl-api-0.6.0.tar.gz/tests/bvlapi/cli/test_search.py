#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains tests for implementation of search implementation.

import unittest.mock as mock

from bvlapi.cli.search import do_search
from bvlapi.data.organizations import Organization


ORG_DATA_A = {'naam': "BBC Antwerp", "guid": "BVBL1001", "stamNr": "103"}
ORG_DATA_B = {'naam': "BC Bergen", "guid": "BVBL1002", "stamNr": "57"}
ORG_DATA_C = {'naam': "Calodar Zoersel", "guid": "BVBL1003", "stamNr": "71"}


def test__search__no_search_terms():
    """ Tests that search fails if no search terms are given.
    """
    exit_code, output = do_search([])
    assert exit_code == 1
    assert output == "unexpected amount of arguments"


def test__search__no_clubs_from_api():
    """ Tests that correct output is generated if no clubs are found.
    """
    with mock.patch("bvlapi.cli.search.get_organizations") as mock_get:
        mock_get.return_value = []
        exit_code, output = do_search(["Antwerp"])
    assert exit_code == 0
    assert output == "could not find any clubs"


def test__search__no_matching_clubs():
    """ Tests that correct output is generated if no matching clubs are found.
    """
    with mock.patch("bvlapi.cli.search.get_organizations") as mock_get:
        mock_get.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        exit_code, output = do_search(["Leuven"])
    assert exit_code == 0
    assert output == "could not find any clubs"


def test__search__one_matching_clubs():
    """ Tests that correct output is generated if a matching club is found.
    """
    with mock.patch("bvlapi.cli.search.get_organizations") as mock_get:
        mock_get.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        exit_code, output = do_search(["Antwerp"])
    assert exit_code == 0
    assert output == "BBC Antwerp:   103    (BVBL1001)"


def test__search__two_matching_clubs():
    """ Tests that correct output is generated if two matching clubs are found.
    """
    with mock.patch("bvlapi.cli.search.get_organizations") as mock_get:
        mock_get.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        exit_code, output = do_search(["BC"])
    assert exit_code == 0
    assert output == "\n".join([
        "BBC Antwerp:   103    (BVBL1001)",
        "BC Bergen:     57     (BVBL1002)",
    ])


def test__search__n_matching_clubs():
    """ Tests that correct output is generated if no matching clubs are found.
    """
    with mock.patch("bvlapi.cli.search.get_organizations") as mock_get:
        mock_get.return_value = [
            Organization(ORG_DATA_A),
            Organization(ORG_DATA_B),
            Organization(ORG_DATA_C),
        ]
        exit_code, output = do_search(["er"])
    assert exit_code == 0
    assert output == "\n".join([
        "BBC Antwerp:       103    (BVBL1001)",
        "BC Bergen:         57     (BVBL1002)",
        "Calodar Zoersel:   71     (BVBL1003)",
    ])
