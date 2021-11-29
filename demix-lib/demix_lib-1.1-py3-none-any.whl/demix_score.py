#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------------------------------------
# Alexis MC - V0.1 - 15/11/2021 Creation of the python DEMIX library
# Alexis MC - V0.2 - 17/11/2021 Added the functions to get single of multiple scores
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------------------------------------------------
import demix_lib.demix_url_handler as dh


# ---------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------

def get_score(demix_tile_name, dem, criterion):
    """
    get score for a single demix tile, dem and criterion
    :param demix_tile_name:
    :param dem:
    :param criterion:
    :return:
    """
    return dh.request_score(demix_tile_name, dem, criterion)


def get_scores(demix_tile_name_list, dem_list, criterion_list):
    """
    :param demix_tile_name_list:
    :param dem_list:
    :param criterion_list:
    :return:
    """
    # handling list
    if type(demix_tile_name_list) is not list:
        demix_tile_name_list = [demix_tile_name_list]
    if type(dem_list) is not list:
        dem_list = [dem_list]
    if type(criterion_list) is not list:
        criterion_list = [criterion_list]

    # for every demix tile, dem , and criterion
    for demix_tile_name in demix_tile_name_list:
        for dem in dem_list:
            for criterion in criterion_list:
                dh.request_score(demix_tile_name, dem, criterion)
