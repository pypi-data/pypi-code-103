#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains tests for making API calls to retrieve information about club.

import pytest
import json

from unittest.mock import patch

from bvlapi.api.org.detail_by_guid import get_detail_by_guid
from bvlapi.api.org.list import get_list
from bvlapi.api.settings import API_BASE_URL
from bvlapi.common.exceptions import InvalidGuid

from tests.files import ORG_DETAIL_BY_GUID_JSON
from tests.files import ORG_LIST_JSON


def test__get_detail_by_guid():
    """ Tests that API is correctly called, and a response is returned.
    """
    with patch("bvlapi.api.org.detail_by_guid.call_api") as mock_call:
        mock_call.return_value = json.loads(ORG_DETAIL_BY_GUID_JSON)
        result = get_detail_by_guid("BVBL1432")
        mock_call.assert_called_with(
            API_BASE_URL + "OrgDetailByGuid?issguid=BVBL1432")

        assert len(result) == 1
        assert result[0]["naam"] == "Antwerp Giants"


def test__get_detail_by_guid__invalid_guid():
    """ Tests that exception is raised when an invalid club GUID is provided.
    """
    with patch("bvlapi.api.org.detail_by_guid.call_api") as mock_call:
        with pytest.raises(InvalidGuid):
            get_detail_by_guid("<NOT A CLUB GUID>")
        mock_call.assert_not_called()


def test__list():
    """ Tests retrieving the list of clubs.
    """
    with patch("bvlapi.api.org.list.call_api") as mock_call:
        mock_call.return_value = json.loads(ORG_LIST_JSON)
        result = get_list()
        mock_call.assert_called_with(API_BASE_URL + "Orglist?p=1")

        assert len(result) == 2
        assert result[0]["naam"] == "Antwerp Giants"
        assert result[1]["naam"] == "BC Machelen-Diegem"
