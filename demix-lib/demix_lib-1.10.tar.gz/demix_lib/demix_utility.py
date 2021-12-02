#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------------------------------------
# Alexis MC - V0.1 - 15/11/2021 Creation of the python DEMIX library
# Alexis MC - V0.2 - 17/11/2021 Added the functions to get demix tile name
#                               Added the functions to print the lists of dem, supported dems and criterions
#                               Added a function to know if a dem/list of dems are supported by the library
#                               Added the functions to get the available dem/supported dem and criterions lists
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------------------------------------------------
import demix_lib.demix_lib_configuration as demix_conf
import demix_lib.demix_url_handler as du

# ---------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------
from demix_lib import demix_colormaps


def demix_help():
    """
    Provides information about the useful functions of the DEMIX lib
    :return: nothing
    """
    print('HELP:\n-function1():allow you to get this information')


def get_demix_tile_name(lon, lat):
    """
    return the demix tile name associated to a longitude and latitude
    :param lon: longitude of the DEMIX tile
    :param lat:  latitude of the DEMIX tile
    :return: demix tile name
    """
    demix_tile_info = du.request_demix_tile_info(lon, lat)
    return demix_tile_info["demixtile"]


def get_demix_tile_info(lon, lat):
    """
    return the demix tile name associated to a longitude and latitude
    :param lon: longitude of the DEMIX tile
    :param lat:  latitude of the DEMIX tile
    :return: demix tile name
    """
    return du.request_demix_tile_info(lon, lat)


def is_dem_supported(dem_name):
    """
    Ask if a specific dem is supported
    :param dem_name:
    :return:
    """
    for dem in demix_conf.supported_dem_list:
        if dem_name == dem:
            return True
    return False


def are_dems_supported(dem_name_list, print_response=False):
    """
    return an array of pair containing the dem as an str and if he is supported or not as a bool
    can print the result
    :param dem_name_list: list of dems or single dem
    :param print_response: Optional bool, will print the response if set to True
    :return: an array of tuples (dem , is_dem_supported)
    """
    are_supported_output = []
    # if we get a single dem, we put it as a list
    if type(dem_name_list) is not list:
        dem_name_list = [dem_name_list]
    # for each dem,
    for asked_dem in dem_name_list:
        supported = False
        for dem in demix_conf.supported_dem_list:
            if asked_dem == dem:
                supported = True
                are_supported_output.append((asked_dem, True))
                if print_response:
                    print(asked_dem + " is supported")

                break
        if not supported:
            are_supported_output.append((asked_dem, False))
            if print_response:
                print(asked_dem + " is not supported")
    return are_supported_output


def print_criterion_list():
    """
    print the available criterion list
    :return:
    """
    print("\nCriterion list :")
    print("---------------------------")
    for criterion in demix_conf.criterion_list:
        print("criterion id   = " + str(criterion[0]))
        print("criterion name = " + str(criterion[1]))
        print("---------------------------")


def print_colormap_list():
    """
    print the available colormap list
    :return:
    """
    print("\nColormap list :")
    print("---------------------------")
    for colormap in demix_colormaps.colormap_list:
        print("Colormap name   = " + str(colormap[0]))
        print("---------------------------")


def print_dem_list():
    """
    print the dem list
    :return:
    """
    print("\nDEM list :")
    print("---------------------------")
    for dem in demix_conf.dem_list:
        print("DEM name = " + dem)
        print("---------------------------")


def print_layer_list():
    """
    print the dem list
    :return:
    """
    print("\nLayer list :")
    print("---------------------------")
    for layer in demix_conf.layer_list:
        print("Layer name = " + layer)
        print("---------------------------")


def print_supported_dem_list():
    """
    print the supported dem list
    :return:
    """
    print("\nsupported DEM list :")
    print("---------------------------")
    for dem in demix_conf.supported_dem_list:
        print("DEM name = " + dem)
        print("---------------------------")


def get_criterion_list():
    """
    get the available criterion list
    :return: the available criterion list
    """
    return demix_conf.criterion_list


def get_criterion_dict():
    """
    get the available criterion list
    :return: the available criterion list
    """
    return dict(demix_conf.criterion_list)


def get_colormap_list():
    """
    get the available colormap list
    :return: the available colormap list
    """
    return demix_colormaps.colormap_list


def get_colormap_dict():
    """
    get the available colormap dictionnary
    :return: the available colormap dictionnary
    """
    return dict(demix_colormaps.colormap_list)


def get_layer_list():
    """
    print the dem list
    :return:
    """
    return demix_conf.layer_list


def get_dem_list():
    """
    get the dem list
    :return: the dem list
    """
    return demix_conf.dem_list


def get_supported_dem_list():
    """
    get the supported dem list
    :return: the supported dem list
    """
    return demix_conf.supported_dem_list


def get_demix_tile_kml_url(lon, lat):
    """
    Ask the server to get the tile name at the desired position
    :param lon: float, longitude of the desired tile
    :param lat: float, latitude of the desired tile
    :return: the DEMIX tile name
    """
    return du.build_demix_tile_kml_url(lon, lat)

