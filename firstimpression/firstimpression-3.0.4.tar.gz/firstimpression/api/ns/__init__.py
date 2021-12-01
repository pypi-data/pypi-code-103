import json
import os
from typing import Any, Dict, List, Optional, Union

from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.json import lst_dict_to_root
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.time import (parse_string_time_to_minutes,
                                  parse_string_to_date, parse_string_to_string)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['ns']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

URL_STATIONS = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations'
URL_DEPARTURES = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures'

MAX_FILE_AGE_DEPARTURES = 60 * 3
MAX_FILE_AGE_STATIONS = 60 * 60 * 24 * 60

STATIONS_JSON_FILENAME = 'stations.json'

##################################################################################################
# SCALA PLAYER
##################################################################################################

scala = ScalaPlayer(NAME)

STATIONS_TEMP_PATH = os.path.join(scala.temp_folder, STATIONS_JSON_FILENAME)
##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    scala.debug('folder name: {}'.format(NAME))

    api_key = scala.variables['subscriptionKey']
    station = scala.variables['station']
    max_journeys = scala.variables['maxJourneys']

    xml_filename = 'departures_{}.xml'.format(station)

    xml_temp_path = os.path.join(scala.temp_folder, xml_filename)

    scala.debug('temp path: {}'.format(xml_temp_path))

    params = {
        'maxJourneys': str(max_journeys),
        'lang': 'nl',
        'station': station
    }

    headers = {
        'Ocp-Apim-Subscription-Key': api_key
    }

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(STATIONS_TEMP_PATH, MAX_FILE_AGE_STATIONS):
        with open(STATIONS_TEMP_PATH, 'w') as file:
            response, is_error = request_json(URL_STATIONS, headers)
            if is_error:
                message = give_error_message(response)
                if response['type'] == 'ERROR':
                    scala.error(message)
                elif response['type'] == 'WARN':
                    scala.warn(message)

                raise SystemExit

            json.dump(response, file)

        scala.install_content(STATIONS_TEMP_PATH)
    else:
        scala.debug('Stations JSON not old enough to update')

    if check_too_old(xml_temp_path, MAX_FILE_AGE_DEPARTURES):

        response, is_error = request_json(URL_DEPARTURES, headers, params)

        if is_error:
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        parsed_departures = get_parsed_departures(response, DATETIME_FORMAT)

        if parsed_departures is None:
            scala.error('Departures are empty', True)
        else:
            temp_path = scala.download_root_temp(lst_dict_to_root(
                parsed_departures), xml_filename)
            scala.install_content(temp_path)
    else:
        scala.debug('Departures file is not old enough to update')


def check_api():
    stations_path = scala.find_content(
        'Content://{}/{}'.format(NAME, STATIONS_JSON_FILENAME))
    stations = json.load(open(stations_path, 'r'))
    svars = scala.variables

    station = svars['station']

    xml_filename = 'departures_{}.xml'.format(station)

    scala.debug('station: {}'.format(station))

    for stat in stations.get('payload', {}):
        if stat.get('code', None) == station:
            svars['station_name'] = stat.get(
                'namen', {}).get('lang', 'Onbekend')
            break

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, xml_filename))

    if check_too_old(file_path, MAX_FILE_AGE_DEPARTURES * 2):
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

def get_departures(response_json: Dict[str, Any]) -> Optional[List[Any]]:
    return response_json.get('payload', {}).get('departures', None)


def get_departure_time(departure: Dict[str, Any]):
    time = departure.get('plannedDateTime', None)
    if time is None:
        return ''
    else:
        return str(time[:-5])


def get_actual_departure_time(departure: Dict[str, Any]):
    time = departure.get('actualDateTime', None)
    if time is None:
        return ''
    else:
        return str(time[:-5])


def get_departure_number(departure: Dict[str, Any]) -> str:
    return departure.get('product', {}).get('number', '')


def get_destination(departure: Dict[str, Any]) -> str:
    return departure.get('direction', '')


def get_train_category(departure: Dict[str, Any]) -> str:
    return departure.get('product', {}).get('longCategoryName', '')


def get_route_text(departure: Dict[str, Any]):
    # Returns string with stations on route in this format: '{station}, {station}, {station}'
    return ', '.join([station.get('mediumName', 'station') for station in departure.get('routeStations', {})])


def get_operator(departure: Dict[str, Any]) -> str:
    return departure.get('product', {}).get('operatorName', '')


def get_planned_track(departure: Dict[str, Any]) -> str:
    if get_actual_track(departure) == '':
        return departure.get('plannedTrack', '')
    else:
        return get_actual_track(departure)


def get_actual_track(departure: Dict[str, Any]) -> str:
    return departure.get('actualTrack', '')


def get_delay(departure: Dict[str, Any], date_format: str):
    try:
        if departure.get('cancelled', False) == True:
            return 'Rijdt niet'
    except KeyError:
        pass

    planned_departure_time = parse_string_to_date(
        get_departure_time(departure), date_format)
    actual_departure_time = parse_string_to_date(
        get_actual_departure_time(departure), date_format)

    if planned_departure_time < actual_departure_time:
        delayed_time = actual_departure_time - planned_departure_time
        delayed_minutes = parse_string_time_to_minutes(str(delayed_time))
        return ''.join(['+', str(delayed_minutes), ' min'])
    else:
        return ''


def get_message(departure: Dict[str, Any]) -> str:
    try:
        message: Union[List[Dict[str, Any]],
                       bool] = departure.get('messages', False)
        if message:
            if isinstance(message, bool):
                raise TypeError('message expected to be List[Any] not bool')
            msg = message[0].get('message', '')
        else:
            msg = ''
    except KeyError:
        msg = ''
    return msg

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def get_parsed_departures(response_json: Dict[str, Any], date_format: str):
    departures = get_departures(response_json)
    parsed_departures: List[Dict[str, str]] = list()

    if departures is None:
        return None

    for departure in departures:
        parsed_departure: Dict[str, str] = dict()
        parsed_departure['departure_number'] = get_departure_number(departure)
        parsed_departure['departure_time'] = parse_string_to_string(
            get_departure_time(departure), date_format, '%H:%M')
        parsed_departure['destination'] = get_destination(departure)
        parsed_departure['train_category'] = get_train_category(departure)
        parsed_departure['route_text'] = get_route_text(departure)
        parsed_departure['operator'] = get_operator(departure)
        parsed_departure['planned_track'] = get_planned_track(departure)
        parsed_departure['delay'] = get_delay(departure, date_format)
        parsed_departure['message'] = get_message(departure)
        parsed_departures.append(parsed_departure)

    return parsed_departures
