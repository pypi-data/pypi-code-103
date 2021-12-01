import os
import xml.etree.ElementTree as ET

from firstimpression.api.request import give_error_message, request
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.time import parse_string_to_string
from requests.models import Response

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['concerts']

MAX_FILE_AGE = 60 * 30

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_NEW = '%a %d %b'
TIME_FORMAT = '%H:%M:%S'
TIME_FORMAT_NEW = '%H:%M'

TAGS = {
    'event': 'results/event',
    'name': 'displayName',
    'type': 'type',
    'age_restriction': 'ageRestriction',
    'start_date': 'start',
    'date': 'date',
    'time': 'time',
    'performance': 'performance/artist',
    'id': 'id',
    'venue': 'venue',
    'location': 'location',
    'city': 'city'
}

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    api_key = scala.variables['api_key']
    area = scala.variables['area']
    max_items = scala.variables['max_items']

    url = 'http://api.songkick.com/api/3.0/metro_areas/{}/calendar.xml'.format(
        area)

    params = {
        'apikey': api_key
    }

    xml_filename = '{}.xml'.format(area)

    xml_temp_path = os.path.join(scala.temp_folder, xml_filename)

    scala.debug('url: {} - temp path: {}'.format(url, xml_temp_path))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(xml_temp_path, MAX_FILE_AGE):
        response = request(url, params=params)

        if not isinstance(response, Response):
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        root = ET.fromstring(response.content)
        new_root = ET.Element("root")

        for event in root.findall(TAGS['event']):
            item = ET.SubElement(new_root, "event")
            ET.SubElement(item, "name").text = get_name(event)
            ET.SubElement(item, "type").text = get_type(event)
            ET.SubElement(
                item, "age_restriction").text = get_age_restriction(event)
            ET.SubElement(item, "date").text = parse_string_to_string(
                get_date(event), DATE_FORMAT, DATE_FORMAT_NEW)
            ET.SubElement(item, "time").text = parse_string_to_string(
                get_time(event), TIME_FORMAT, TIME_FORMAT_NEW)
            ET.SubElement(item, "performers").text = get_performers(event)
            ET.SubElement(item, "photo").text = get_photo(event)
            ET.SubElement(item, "venue").text = get_venue(event)
            ET.SubElement(item, "location").text = get_location(event)

            if len(new_root) == max_items:
                scala.debug('max amount of items breaking')
                break

        temp_path = scala.download_root_temp(new_root, xml_filename)
        scala.install_content(temp_path)

    else:
        scala.debug('File not old enough to update')


def check_api():
    svars = scala.variables

    area = svars['area']

    xml_filename = '{}.xml'.format(area)

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, xml_filename))

    if check_too_old(file_path, MAX_FILE_AGE * 2):
        svars['skipscript'] = True
        scala.debug('file too old')
    else:
        svars['skipscript'] = False

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


def get_photo(event):
    performance = get_performances(event)[0]

    artist_id = get_artist_id(performance)
    link = 'http://images.sk-static.com/images/media/profile_images/artists/{}/large_avatar'.format(
        artist_id)

    temp_path = scala.download_media_temp(link, '{}.jpg'.format(artist_id))
    media_link = scala.install_content(temp_path)

    if media_link is None:
        scala.debug('No image found using placeholder instead')
        return 'Content:\\placeholders\\img.png'
    else:
        return media_link

##################################################################################################
# GET FUNCTIONS
##################################################################################################


def get_name(event):
    return event.get(TAGS['name'], '')


def get_type(event):
    return event.get(TAGS['type'], '')


def get_age_restriction(event):
    return event.get(TAGS['age_restriction'], '')


def get_start_date(event):
    return event.find(TAGS['start_date'])


def get_date(event):
    start_date = get_start_date(event)

    if not start_date is None:
        return start_date.get(TAGS['date'], '')
    else:
        return ''


def get_time(event):
    start_date = get_start_date(event)

    if not start_date is None:
        return start_date.get(TAGS['time'], '')
    else:
        return ''


def get_performances(event):
    return event.findall(TAGS['performance'])


def get_artist_id(performance):
    return performance.get(TAGS['id'], None)


def get_artist_name(performance):
    return performance.get(TAGS['name'], None)


def get_performers(event):
    performances = get_performances(event)
    performers = list()

    for performance in performances:
        artist_id = get_artist_id(performance)

        if not artist_id is None:
            performers.append(get_artist_name(performance))

    return ' + '.join(performers)


def get_venue(event):
    return event.find(TAGS['venue']).get(TAGS['name'], '')


def get_location(event):
    return event.find(TAGS['location']).get(TAGS['city'], '').split(',').pop(0)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
