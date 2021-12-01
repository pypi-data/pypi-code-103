import os
import xml.etree.ElementTree as ET

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

NAME = APIS['twitter']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATETIME_FORMAT_NEW = '%d %B %Y'

URL = 'https://fi-api.io/twitter_post/'

XML_FILENAME = 'twitter.xml'

MAX_FILE_AGE = 60 * 5

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

XML_TEMP_PATH = os.path.join(scala.temp_folder, XML_FILENAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    api_key = scala.variables['api_key']
    max_items = scala.variables['max_items']

    scala.debug('folder name: {}'.format(NAME))
    scala.debug('file path temp: {}'.format(XML_TEMP_PATH))

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    params = {
        'number_of_posts': max_items
    }

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        response_json, is_error = request_json(URL, headers, params, False)

        if is_error:
            message = give_error_message(response_json)
            if response_json['type'] == 'ERROR':
                scala.error(message)
            elif response_json['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        root = ET.Element("root")

        for post in response_json:
            root.append(parse_post(post))

        temp_path = scala.download_root_temp(root, XML_FILENAME)
        scala.install_content(temp_path)
    else:
        scala.debug('File not old enough to update')


def check_api():
    svars = scala.variables

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, XML_FILENAME))

    if check_too_old(file_path, MAX_FILE_AGE * 2):
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

def get_likes(post):
    return post.get('likes', 0)


def get_message(post):
    return post.get('message', '')


def get_creation_date(post):
    return post.get('created_at', '')


def get_image(post):
    url = post.get('image', None)
    if url is None:
        scala.debug('No image found using placeholder instead')
        return 'Content:\\placeholders\\img.png'
    else:
        temp_path = scala.download_media_temp(url)
        return scala.install_content(temp_path)


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def parse_post(post):
    item = ET.Element("item")
    ET.SubElement(item, "likes").text = str(get_likes(post))
    ET.SubElement(item, "message").text = remove_emoji(get_message(post))
    ET.SubElement(item, "created_time").text = parse_string_to_string(
        get_creation_date(post), DATETIME_FORMAT, DATETIME_FORMAT_NEW)
    ET.SubElement(item, "image").text = get_image(post)
    return item
