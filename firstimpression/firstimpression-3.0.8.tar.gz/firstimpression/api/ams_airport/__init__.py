import datetime
import json
import os
from typing import Any, Dict, List, Union

from firstimpression.api.request import request
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.json import lst_dict_to_root
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.time import parse_date_to_string, parse_string_to_string
from requests import Response

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['schiphol']

URL_FLIGHTS = 'https://api.schiphol.nl/public-flights/flights'
URL_STATIONS = 'https://api.schiphol.nl/public-flights/destinations'

STATIONS_JSON_FILENAME = 'stations.json'
STATIONS_MAX_FILE_AGE = 60 * 60 * 24 * 7 * 4

FLIGHTS_XML_FILENAME = 'flights.xml'
FLIGHTS_MAX_FILE_AGE = 60 * 10

PURGE_DIRECTORIES_DAYS = 7 * 4

FLIGHTS_MAX = 100

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
SCHEDULE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000'
TIME_FORMAT = '%H:%M'

RESOURCE_VERSION = 'v4'

DEPARTING_STATUS = {
    'SCH': 'Flight scheduled',
    'DEL': 'Delayed',
    'WIL': 'Wait in Lounge',
    'GTO': 'Gate Open',
    'BRD': 'Boarding',
    'GCL': 'Gate Closing',
    'GTD': 'Gate closed',
    'DEP': 'Departed',
    'CNX': 'Cancelled',
    'GCH': 'Gate Change',
    'TOM': 'Tomorrow'
}

HEADERS = {
    'Accept': 'application/json',
    'ResourceVersion': RESOURCE_VERSION
}

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

XML_TEMP_PATH_FLIGHTS = os.path.join(scala.temp_folder, FLIGHTS_XML_FILENAME)
JSON_TEMP_PATH_STATIONS = os.path.join(
    scala.temp_folder, STATIONS_JSON_FILENAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    scala.debug('folder name: {}'.format(NAME))
    scala.debug('file paths: temp -> {}, local -> {}'.format(
        XML_TEMP_PATH_FLIGHTS, scala.content_folder))

    HEADERS['app_id'] = scala.variables['api_id']
    HEADERS['app_key'] = scala.variables['api_key']

    scala.debug('headers: {}'.format(HEADERS))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder],
                      max_days=PURGE_DIRECTORIES_DAYS)
    update_placeholders()

    if check_too_old(JSON_TEMP_PATH_STATIONS, STATIONS_MAX_FILE_AGE):
        page = 0
        params: Dict[str, Union[int, str]] = dict()
        stations: Dict[str, str] = dict()

        for _ in range(100000):
            params['page'] = page
            response = request(URL_STATIONS, HEADERS, params)

            if not isinstance(response, Response):
                scala.debug(
                    'request {}: {} -> {}'.format(response['type'], response['reason'], response['message']))
                scala.debug('No more pages found for stations')
                break

            stations.update(get_stations(response.json()))

            page += 1

        scala.debug('page of stations: {}'.format(page))

        if page == 99999:
            scala.warn(
                'Something went probably wrong when downloading stations')

        with open(JSON_TEMP_PATH_STATIONS, 'w') as file:
            json.dump(stations, file)

        scala.install_content(JSON_TEMP_PATH_STATIONS)
    else:
        scala.debug('Station file not old enough')

    if check_too_old(XML_TEMP_PATH_FLIGHTS, FLIGHTS_MAX_FILE_AGE):
        page = 0
        params = {
            'sort': '+scheduleDateTime',
            'flightDirection': 'D',
            'searchDateTimeField': 'scheduleDateTime',
            'fromDateTime': parse_date_to_string(datetime.datetime.now(), DATETIME_FORMAT),
            'toDateTime': parse_date_to_string(datetime.datetime.now(), DATE_FORMAT) + 'T23:59:59'
        }
        flights: List[Dict[str, str]] = list()

        scala.debug(str(params))

        stations_path = scala.find_content(
            'Content://{}/{}'.format(NAME, STATIONS_JSON_FILENAME))

        destinations = json.load(open(stations_path, 'r'))

        for _ in range(100000):
            params['page'] = page
            response = request(URL_FLIGHTS, HEADERS, params)

            if not isinstance(response, Response):
                scala.debug(
                    'request {}: {} -> {}'.format(response['type'], response['reason'], response['message']))
                scala.debug('No more flights found.')
                break

            flights = parse_flights(flights, destinations, response.json())

            if len(flights) == FLIGHTS_MAX:
                scala.debug('Max amount of flights')
                break

            page += 1

        scala.debug('page of flights: {}'.format(page))
        scala.debug(str(flights))

        if len(flights) == 0:
            scala.warn('No flights saved')

        if page == 99999:
            scala.warn('Something went probably wrong when downloading flights')

        temp_path = scala.download_root_temp(
            lst_dict_to_root(flights), XML_TEMP_PATH_FLIGHTS)
        scala.install_content(temp_path)
    else:
        scala.debug('File not old enough flights')


def check_api():
    svars = scala.variables

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, FLIGHTS_XML_FILENAME))

    if check_too_old(file_path, FLIGHTS_MAX_FILE_AGE*2):
        svars['skipscript'] = True
        scala.debug('file too old')
    else:
        svars['skipscript'] = False

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_stations(response: Dict[str, List[Dict[str, Any]]]):
    stations: Dict[str, str] = dict()
    for destination in response.get('destinations', []):
        if not destination.get('iata', 'null') == 'null' and not destination.get('iata', None) is None:
            name = destination.get('publicName', None)
            if not name is None:
                full_name = name.get('english', None)
                if not full_name is None:
                    stations[destination['iata']] = full_name

    return stations


def get_flight_route(flight: Dict[str, Dict[str, str]], destinations: Dict[str, str]):

    route: List[str] = list()

    for elem in flight.get('route', {}).get('destinations', 'null'):
        location = destinations.get(elem, 'Onbekend')
        if location == 'Onbekend':
            scala.debug('location route: {}'.format(elem))
        route.append(location)

    return ', '.join(route)


def get_departure_time(flight: Dict[str, Any]):
    dt = flight.get('scheduleDateTime', None)
    if dt is None:
        return ''
    else:
        dt = dt[:-6]
        return parse_string_to_string(dt, SCHEDULE_DATETIME_FORMAT, TIME_FORMAT)


def get_flight_number(flight: Dict[str, Any]) -> str:
    return flight.get('flightName', 'Onbekend')


def get_flight_status(flight: Dict[str, Any]) -> str:
    status = flight.get('publicFlightState', {}).get(
        'flightStates', ['null'])[0]

    return DEPARTING_STATUS.get(status, 'Unknown')

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_flights(flights: List[Dict[str, str]], destinations: Dict[str, str], response: Dict[str, List[Dict[str, Any]]]):

    for flight_info in response.get('flights', []):
        flight: Dict[str, str] = dict()
        skip = False

        flight['route'] = get_flight_route(flight_info, destinations)
        flight['departure_time'] = get_departure_time(flight_info)
        flight['flight_number'] = get_flight_number(flight_info)
        flight['status'] = get_flight_status(flight_info)

        for i in range(len(flights)):
            if flights[i]['route'] == flight['route'] and flights[i]['departure_time'] == flight['departure_time'] and flights[i]['status'] == flight['status']:
                flights[i]['flight_number'] += ', ' + flight['flight_number']
                skip = True
                scala.debug('flight {} is same as flight {}'.format(
                    flight['flight_number'], flights[i]['flight_number']))

        if not skip:
            flights.append(flight)

        if len(flights) == FLIGHTS_MAX:
            scala.debug('break because max amount of fligths reached')
            break

    return flights
