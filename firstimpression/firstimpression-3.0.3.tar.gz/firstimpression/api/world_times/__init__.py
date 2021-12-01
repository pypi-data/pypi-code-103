import datetime
import glob
import os
from firstimpression.api.request import give_error_message, request_json

import pytz
from firstimpression.constants import APIS, IMG_EXTENSIONS
from firstimpression.file import check_too_old, create_directories, purge_directories
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.time import parse_date_to_string

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['world_times']

URL = 'https://fi-api.io/world_times'

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=10)
    update_placeholders()

    local_images = glob.glob(os.path.join(scala.content_folder, '*.png'))

    if len(local_images) == 0:
        download_images(URL, IMG_EXTENSIONS)


def check_api():
    timezones = {
        'auckland': 'Pacific/Auckland',
        'amsterdam': 'Europe/Amsterdam',
        'bangkok': 'Asia/Bangkok',
        'calgary': 'America/Edmonton',
        'dubai': 'Asia/Dubai',
        'guangzhou': 'Asia/Hong_Kong',
        'gunzenhausen': 'Europe/Berlin',
        'hanko': 'Europe/Helsinki',
        'london': 'Europe/London',
        'moscow': 'Europe/Moscow',
        'new_york': 'America/New_York',
        'nieuwkuijk': 'Europe/Amsterdam',
        'oss': 'Europe/Amsterdam',
        'paris': 'Europe/Paris',
        'reykjavik': 'Atlantic/Reykjavik',
        'riyadh': 'Asia/Riyadh',
        'santiago': 'America/Santiago',
        'scherpenzeel': 'Europe/Amsterdam',
        'seattle': 'America/Los_Angeles',
        'shanghai': 'Asia/Shanghai',
        'stockholm': 'Europe/Stockholm',
        'sydney': 'Australia/Sydney',
        'tilburg': 'Europe/Amsterdam',
        'tokyo': 'Asia/Tokyo',
        'vlijmen': 'Europe/Amsterdam',
    }

    svars = scala.variables

    timezones_to_get = svars['locations'].strip(';').split(';')

    timezones_to_return = []
    times_to_return = []
    images = []

    for tz in timezones_to_get:
        if tz in timezones.keys():
            timezones_to_return.append(tz.replace('_', ' ').title())
            images.append('Content:\\{}\\{}.png'.format(NAME, tz.capitalize()))
            times_to_return.append(parse_date_to_string(
                datetime.datetime.now(pytz.timezone(timezones[tz])), '%H:%M'))
        else:
            scala.error('timezone of {} not in list'.format(tz))

    svars['locations_list'] = timezones_to_return
    svars['times_list'] = times_to_return
    svars['images_list'] = images


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


def list_images(url_icons, extensions):

    response, is_error = request_json(url_icons)

    if is_error:
        message = give_error_message(response)
        if response['type'] == 'ERROR':
            scala.error(message)
        elif response['type'] == 'WARN':
            scala.warn(message)

        raise SystemExit

    elements = response.get('data', [])
    elements = [elem for elem in elements if '.' +
                elem.split('.')[-1] in extensions]

    return elements


def download_images(url, extensions):
    links = list_images(url, extensions)

    for link in links:
        scala.debug('icon link: {}'.format(link))
        file_name = link.split('/')[-1]
        if check_too_old(os.path.join(scala.temp_folder, file_name), 10):
            temp_path = scala.download_media_temp(link)
            scala.install_content(temp_path)

##################################################################################################
# GET FUNCTIONS
##################################################################################################


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
