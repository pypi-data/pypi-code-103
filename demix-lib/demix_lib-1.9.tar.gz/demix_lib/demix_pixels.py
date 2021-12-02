#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------------------------------------
# Alexis MC - V0.1 - 15/11/2021 Creation of the python DEMIX library
# Alexis MC - V0.2 - 17/11/2021 Added function prototype
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------------------------------------------------
import demix_lib.demix_url_handler as dh


# ---------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------

def download_layer(demix_tile_name, dem, layer, print_request=False):
    """
    Allow you to download a specific layer as a geotiff
    :param print_request: True if you want to see the html request used to get the data
    :param demix_tile_name: the demix tile name
    :param dem: the dem from which you want to get a layer
    :param layer: the layer name
    :return: the wanted layer
    """
    return dh.request_pixels(tile_name=demix_tile_name, dem=dem, layer=layer, print_request=print_request)
