#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains function to call API for a list of all clubs.

from bvlapi.api.call import call_api
from bvlapi.api.settings import API_BASE_URL


def get_list():
    """ Calls API to retrieve list of all basketball clubs.

    :rtype: [dict]
    :return: a list of dictionaries containing basic information about clubs

    :raise ApiCallFailed: something went wrong while calling API
    """
    url = API_BASE_URL + "Orglist?p=1"
    return call_api(url)
