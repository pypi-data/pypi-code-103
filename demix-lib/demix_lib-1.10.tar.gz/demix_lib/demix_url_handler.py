#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------------------------------------
# Alexis MC - V0.1 - 15/11/2021 Creation of the python DEMIX library
# Alexis MC - V0.2 - 17/11/2021 Added the functions to request pixels, score, and DEMIX tile name to the API
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------------------------------------------------
import urllib3
import certifi
import json

# ---------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------
# BASE_URL : Allow you to define product's download url
BASE_URL = "http://visioterra.org:8080/DEMIXService/DEMIXService?"
# VERIFY : Put False if you don't want to check website certificate, put True ether way
VERIFY = False


def byte_to_json(bytes_value):
    """
    transform a byte response to a json response
    :param bytes_value: the byte response
    :return:
    """
    # Decode UTF-8 bytes to Unicode, and convert single quotes
    # to double quotes to make it valid JSON
    my_json = bytes_value.decode('utf8').replace("'", '"')
    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)
    return data


def request_pixels(tile_name, dem, layer, print_request=False):
    """
    Ask the server to get the geotiff layer corresponding to a specific layer
    :param print_request: False if you dont want to see the request made to the server, True to see
    :param tile_name: str, a tile name, for example "N64ZW019"
    :param dem: str, a dem name, for example "SRTMGL1"
    :param layer: str, a layer name, for example "SourceMask"
    :return: the request response
    """
    request = BASE_URL + "service=getPixels" + "&DEMIXTile=" + tile_name + "&DEM=" + dem + "&Layer=" + layer
    if print_request:
        print(request)
    return send_request(request)


def request_score(tile_name, dem, criterion, print_request=False):
    """
    Ask the server to get the score in the chosen DEMIX tile and DEM for a specific criterion
    :param print_request: true if you want to look at the sent request
    :param tile_name: str, a tile name, for example "N64ZW019"
    :param dem: str, a dem name, for example "SRTMGL1"
    :param criterion: str, a criterion name, for example "A01"
    :return: the request response
    """
    request = BASE_URL + "service=getScore" + "&DEMIXTile=" + tile_name + "&DEM=" + dem + "&Criterion=" + criterion
    if print_request:
        print(request)
    return send_request(request)


def request_demix_tile_info(lon, lat):
    """
    Ask the server to get the tile name at the desired position
    :param lon: float, longitude of the desired tile
    :param lat: float, latitude of the desired tile
    :return: the DEMIX tile name
    """
    request = BASE_URL + "service=getDEMIXTileInfo" + "&lon=" + str(lon) + "&lat=" + str(lat)
    return send_request(request)


def send_request(request):
    """
    lunch the request and return the content as json
    :param request: the request url
    :return: the response as json
    """
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request('GET', request)
    http.clear()
    return byte_to_json(response.data)


def build_demix_tile_kml_url(lon, lat):
    """
    Ask the server to get the tile name at the desired position
    :param lon: float, longitude of the desired tile
    :param lat: float, latitude of the desired tile
    :return: the DEMIX tile name
    """
    request = BASE_URL + "service=getDEMIXTileInfo" + "&lon=" + str(lon) + "&lat=" + str(lat) + "&format=KML"
    return request
