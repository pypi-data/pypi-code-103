#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains class used to hold basic information about an organization.

from bvlapi.data.parse import use_fallback_value
from bvlapi.guid.club import is_club_guid


class Organization:
    """ Used to represent and organize information about an organization.

    :ivar str name: name of organization
    :ivar str guid: GUID of organization
    :ivar str stam: stamnr of organization
    """

    def __init__(self, organization_data):
        """ Initializes a new instance of Organization based on information
            retrieved through API.

        :param dict organization_data: contains information about organization
        """
        self.name = parse_name(organization_data)
        self.guid = parse_guid(organization_data)
        self.stam = parse_stam(organization_data)


@use_fallback_value("<UNKNOWN CLUB NAME>")
def parse_name(organization_data):
    """ Used to parse name of organization.
    """
    return str(organization_data["naam"])


@use_fallback_value("<UNKNOWN CLUB GUID>")
def parse_guid(organization_data):
    """ Used to parse GUID of organization.
    """
    if not is_club_guid(organization_data["guid"]):
        return "<INVALID CLUB GUID>"
    return str(organization_data["guid"])


@use_fallback_value("<UNKNOWN STAM NR>")
def parse_stam(organization_data):
    """ Used to parse stamnummer of organization.
    """
    return str(organization_data["stamNr"])
