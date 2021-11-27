#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Contains function used to retrieve list of organizations.

from bvlapi.data.organizations.organization import Organization
from bvlapi.api.org.list import get_list


def get_organizations():
    """ Queries API for a list of all basketball organizations registered
        with Basketbal Vlaanderen.

    :return: list of basketball organizations
    :rtype: [Organization]
    """
    organizations = []
    for organization_data in get_list():
        organizations.append(Organization(organization_data))
    return list(sorted(organizations, key=lambda o: o.guid))
