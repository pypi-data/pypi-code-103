import os
import xml.etree.ElementTree as ET
from typing import Any, Dict

from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.text import remove_emoji
from firstimpression.time import parse_string_to_string

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['facebook']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATETIME_FORMAT_NEW = '%d %B %Y'

URL = 'https://fi-api.io/socials/facebook/posts/'
BASE_URL_IMAGES = 'https://socials-bucket.s3.eu-central-1.amazonaws.com'

XML_FILENAME = 'facebook.xml'

##################################################################################################
# LOGGING
##################################################################################################

scala = ScalaPlayer(NAME)

XML_TEMP_PATH = os.path.join(scala.temp_folder, XML_FILENAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    scala.debug('folder name: {}'.format(NAME))

    max_file_age = 60 * scala.variables['max_minutes']
    api_key = scala.variables['api_key']
    max_characters = scala.variables['max_chars']
    max_items = scala.variables['max_items']

    scala.debug(
        'max_file_age: {} - temp path: {}'.format(max_file_age, XML_TEMP_PATH))

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    params = {
        'number_of_posts': max_items
    }

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(XML_TEMP_PATH, max_file_age):
        response_json, is_error = request_json(URL, headers, params, False)

        if is_error:
            message = give_error_message(response_json)
            if response_json['type'] == 'ERROR':
                scala.error(message)
            elif response_json['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit
        else:
            response_json: Any

        root = ET.Element("root")

        for post in response_json:
            item = ET.SubElement(root, "item")
            ET.SubElement(item, "likes").text = str(
                get_reactions(post))
            ET.SubElement(item, "message").text = crop_message(
                remove_emoji(get_message(post)), max_characters)
            ET.SubElement(item, "created_time").text = parse_string_to_string(
                get_creation_date(post), DATETIME_FORMAT, DATETIME_FORMAT_NEW)

            thumbnail_url = get_image(post)
            if thumbnail_url is None:
                scala.debug('image not found using placeholder')
                media_link = 'Content:\\placeholders\\img.png'
            else:
                scala.debug(thumbnail_url)
                temp_path = scala.download_media_temp(thumbnail_url)
                media_link = scala.install_content(temp_path)

            ET.SubElement(item, "image").text = media_link

        temp_path = scala.download_root_temp(root, XML_FILENAME)
        scala.install_content(temp_path)
    else:
        scala.debug('File not old enough to download new info')


def check_api():
    svars = scala.variables

    max_file_age = 60 * svars['max_minutes'] + 2

    scala.debug('max_file_age: {}'.format(max_file_age))

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, XML_FILENAME))

    scala.debug('local path: {}'.format(file_path))

    if check_too_old(file_path, max_file_age):
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

def get_image(post: Dict[str, Any]):
    return post.get('media', None)


def get_reactions(post: Dict[str, Any]):
    return post.get('likes', 0)


def get_message(post: Dict[str, Any]):
    return post.get('message', '')


def get_creation_date(post: Dict[str, Any]):
    creation_date = post.get('created_at', None)
    if creation_date is None:
        return ''
    else:
        return str(creation_date[:19])

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def crop_message(text: str, max_length: int):
    if len(text) > max_length:
        return text[:max_length-3] + "...\nLees verder op Facebook"
    else:
        return text
