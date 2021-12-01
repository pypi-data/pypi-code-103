import os
import xml.etree.ElementTree as ET

from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.json import lst_dict_to_root
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.xml import path_to_root
from geopy import distance

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['traffic']

EXCLUDE_FROM_XML = 'coordinates'

XML_FILE_NAME_LONGEST = 'longest_jams.xml'
XML_FILE_NAME_CLOSEST = 'closest_jams.xml'

MAX_FILE_AGE = 60 * 10

URL = 'https://api.rwsverkeersinfo.nl/api/traffic'

PARAMS = {
    'query_type': 'overview'
}

HEADERS = {
    'cache-control': 'no-cache',
    'Accept': 'application/json'
}

TAGS = {
    'circumstances': 'obstructions'
}

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

XML_TEMP_PATH_LONGEST = os.path.join(scala.temp_folder, XML_FILE_NAME_LONGEST)
XML_TEMP_PATH_CLOSEST = os.path.join(scala.temp_folder, XML_FILE_NAME_CLOSEST)


##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    jam_type = 4
    max_closest = scala.variables['max_closest_jams']
    max_longest = scala.variables['max_longest_jams']
    own_coordinates = {'latitude': float(
        scala.variables['latitude']), 'longitude': float(scala.variables['longitude'])}
    only_highways = scala.variables['only_highways']

    scala.debug('folder name: {}'.format(NAME))
    scala.debug('file paths - temp long: {} - temp close: {}'.format(
        XML_TEMP_PATH_LONGEST, XML_TEMP_PATH_CLOSEST))
    scala.debug('max_close: {} - max_long: {}'.format(max_closest, max_longest))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if (check_too_old(XML_TEMP_PATH_LONGEST, MAX_FILE_AGE) and max_longest > 0) or (check_too_old(XML_TEMP_PATH_CLOSEST, MAX_FILE_AGE) and max_closest > 0):
        traffic_info, is_error = request_json(URL, HEADERS, PARAMS)

        if is_error:
            message = give_error_message(traffic_info)
            if traffic_info['type'] == 'ERROR':
                scala.error(message)
            elif traffic_info['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        circumstances = parse_circumstances(get_circumstances(
            traffic_info), own_coordinates, only_highways)
        jams = get_jams(circumstances, jam_type)

        if check_too_old(XML_TEMP_PATH_LONGEST, MAX_FILE_AGE) and max_longest > 0:
            sorted_jams = sort_longest_jams(jams)
            sorted_jams = [{key: value for key, value in d.items(
            ) if key != EXCLUDE_FROM_XML} for d in sorted_jams]
            root = lst_dict_to_root(sorted_jams[:max_longest])

            ET.SubElement(root, "total_circumstances").text = str(
                get_total_jams(jams))
            ET.SubElement(
                root, "total_circumstances_string").text = get_total_jams_str(jams)
            ET.SubElement(root, "total_length").text = str(
                get_total_jam_length(traffic_info))
            ET.SubElement(root, "total_length_string").text = get_total_length_string(
                traffic_info)
            ET.SubElement(
                root, "total_delay_string").text = calculate_total_delay_str(jams)

            temp_path = scala.download_root_temp(root, XML_FILE_NAME_LONGEST)
            scala.install_content(temp_path)
        else:
            scala.debug('Longest xml does not need to be updated')

        if check_too_old(XML_TEMP_PATH_CLOSEST, MAX_FILE_AGE) and max_closest > 0:
            sorted_jams = sort_closest_jams(jams)
            sorted_jams = [{key: value for key, value in d.items(
            ) if key != EXCLUDE_FROM_XML} for d in sorted_jams]
            root = lst_dict_to_root(sorted_jams[:max_closest])

            ET.SubElement(root, "total_circumstances").text = str(
                get_total_jams(jams))
            ET.SubElement(
                root, "total_circumstances_string").text = get_total_jams_str(jams)
            ET.SubElement(root, "total_length").text = str(
                get_total_jam_length(traffic_info))
            ET.SubElement(root, "total_length_string").text = get_total_length_string(
                traffic_info)
            ET.SubElement(
                root, "total_delay_string").text = calculate_total_delay_str(jams)

            temp_path = scala.download_root_temp(root, XML_FILE_NAME_CLOSEST)
            scala.install_content(temp_path)
        else:
            scala.debug('Closest xml does not need to be updated')
    else:
        scala.debug('Files are not updated')


def check_api():
    svars = scala.variables

    svars['skipscript'] = False

    min_closest = svars['min_closest']
    min_longest = svars['min_longest']

    if min_closest > 0:
        file_path = scala.find_content(
            'Content://{}/{}'.format(NAME, XML_FILE_NAME_CLOSEST))

        if check_too_old(file_path, MAX_FILE_AGE * 2):
            svars['skipscript'] = True
            scala.debug('file too old closest')
        else:
            svars['skipscript'] = False

            if path_to_root(file_path).findtext('total_circumstances', 0) == 0:
                svars['skipscript'] = True
                scala.debug('no traffic jams at the moment')

    if not svars['skipscript'] and min_longest > 0:
        file_path = scala.find_content(
            'Content://{}/{}'.format(NAME, XML_FILE_NAME_LONGEST))

        if check_too_old(file_path, MAX_FILE_AGE * 2):
            svars['skipscript'] = True
            scala.debug('file too old closest')
        else:
            svars['skipscript'] = False

            if path_to_root(file_path).findtext('total_circumstances', 0) == 0:
                svars['skipscript'] = True
                scala.debug('no traffic jams at the moment')

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_circumstances(traffic_info):
    return traffic_info.get(TAGS['circumstances'], {})


def get_reason(circumstance):
    return circumstance.get('cause', '')


def get_area_detail(circumstance):
    return circumstance.get('locationText', '')


def get_event(circumstance):
    return circumstance.get('title', '')


def get_description(circumstance):
    return circumstance.get('description', '')


def get_type(circumstance):
    return circumstance.get('obstructionType', 0)


def get_direction_text(circumstance):
    return circumstance.get('directionText', None)


def get_from(circumstance):
    text = get_direction_text(circumstance)
    if text is None:
        return ''
    else:
        try:
            return text.split(' - ')[0]
        except IndexError:
            return ''


def get_to(circumstance):
    text = get_direction_text(circumstance)
    if text is None:
        return ''
    else:
        try:
            return text.split(' - ')[1]
        except IndexError:
            return ''


def get_total_jams(jams):
    return len(jams)


def get_total_jams_str(jams):
    total = get_total_jams(jams)

    temp = '{} file'.format(total)

    if total != 1:
        temp += 's'

    return temp


def get_road_type(circumstance):
    road = get_road(circumstance)

    if road is None:
        return ''
    else:
        return road[0]


def get_road(circumstance):
    return circumstance.get('roadNumber', None)


def get_road_number(circumstance):
    road = get_road(circumstance)

    if road is None:
        return ''
    else:
        return road[1:]


def get_length(circumstance):
    total_length = circumstance.get('total_length', None)
    if total_length is None:
        return ''
    else:
        return int(total_length)


def get_length_string(circumstance):
    length = get_length(circumstance)
    if length != '':
        return '{} km'.format(length/1000)
    else:
        return 'onbekend'


def get_delay(circumstance):
    total_length = circumstance.get('delay', None)

    if total_length is None:
        return ''
    else:
        return int(total_length)


def get_delay_string(circumstance):
    delay = get_delay(circumstance)

    if delay is None:
        return ''
    else:
        return '+{} min'.format(delay)


def get_jams(circumstances, jam_type):
    jams = list()
    for circumstance in circumstances:
        if circumstance.get('type', 1) == jam_type:
            jams.append(circumstance)
    return jams


def get_longitude(circumstance):
    return circumstance.get('longitude', '')


def get_latitude(circumstance):
    return circumstance.get('latitude', '')


def get_coordinates(circumstance):
    return {'longitude': get_longitude(circumstance), 'latitude': get_latitude(circumstance)}


def get_total_jam_length(traffic_info):
    return traffic_info.get('totalLengthOfJams', 0) / 1000


def get_total_length_string(traffic_info):
    return '{} km'.format(get_total_jam_length(traffic_info))


def get_only_highways(parsed_circumstances):
    specific_circumstances = list()
    for circumstance in parsed_circumstances:
        if circumstance['road_type'] == 'A':
            specific_circumstances.append(circumstance)
    return specific_circumstances


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_circumstances(circumstances, own_coordinates, only_highways):
    parsed_circumstances = list()
    for circumstance in circumstances:
        parsed_circumstances.append(
            parse_circumstance(circumstance, own_coordinates))

    if only_highways:
        return get_only_highways(parsed_circumstances)
    else:
        return parsed_circumstances


def parse_circumstance(circumstance, own_coordinates):
    # Parses JSON from API to own format. Junk data is removed.
    parsed_circumstance = dict()

    parsed_circumstance['road_type'] = get_road_type(circumstance)
    parsed_circumstance['road'] = get_road(circumstance)
    parsed_circumstance['road_number'] = get_road_number(circumstance)
    parsed_circumstance['from'] = get_from(circumstance)
    parsed_circumstance['to'] = get_to(circumstance)
    parsed_circumstance['length'] = get_length(circumstance)
    parsed_circumstance['length_string'] = ''
    parsed_circumstance['reason'] = get_reason(circumstance)
    parsed_circumstance['area_detail'] = get_area_detail(circumstance)
    parsed_circumstance['event'] = get_event(circumstance)
    parsed_circumstance['description'] = get_description(circumstance)
    parsed_circumstance['type'] = get_type(circumstance)
    parsed_circumstance['total_delay'] = get_delay_string(circumstance)
    parsed_circumstance['coordinates'] = get_coordinates(circumstance)

    parsed_circumstance['distance_to_circumstance'] = calculate_distance_to_circumstance(
        own_coordinates, parsed_circumstance['coordinates'])

    return parsed_circumstance


def sort_longest_jams(jams):
    # Sorts longest jams starting with longest to shortest
    return sorted(jams, key=lambda i: i['length'], reverse=True)


def sort_closest_jams(jams):
    # Sorts jams that are closest to own location
    return sorted(jams, key=lambda i: i['distance_to_circumstance'])


def calculate_distance_to_circumstance(from_coordinates, to_coordinates):
    # Calculates distance from one coordinate to another (WATCH OUT: straight line, so no roads taken into account)
    if not from_coordinates or not to_coordinates:
        return ''

    coords_1 = (from_coordinates['latitude'], from_coordinates['longitude'])
    coords_2 = (to_coordinates['latitude'], to_coordinates['longitude'])

    return distance.distance(coords_1, coords_2).km


def calculate_total_delay_str(jams):
    total_delay = 0
    for jam in jams:
        delay = jam.get('total_delay', '')
        if delay == '':
            continue
        else:
            total_delay += int(delay.split(' ').pop(0))

    if total_delay > 60:
        return '{}+ uur'.format(int(total_delay / 60))
    else:
        return '{} min'.format(int(total_delay))
