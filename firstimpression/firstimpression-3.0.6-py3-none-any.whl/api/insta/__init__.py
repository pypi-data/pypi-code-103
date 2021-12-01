import os
import xml.etree.ElementTree as ET
from typing import Any, Dict

from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import APIS, DUTCH_INDEX
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.text import remove_emoji
from firstimpression.time import parse_string_to_string

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['insta']

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

URL = 'https://fi-api.io/socials/instagram/posts/'
BASE_URL_IMAGES = 'https://socials-bucket.s3.eu-central-1.amazonaws.com'

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    scala.debug('folder name: {}'.format(NAME))

    api_key = scala.variables['api_key']
    max_characters = scala.variables['max_chars']
    max_items = scala.variables['max_items']
    input_tags = scala.variables['tags']

    max_file_age = 60 * scala.variables['max_minutes']

    scala.debug('max_file_age: {}'.format(max_file_age))

    if scala.language == DUTCH_INDEX:
        datetime_format_new = '%d %B %Y'
    else:
        datetime_format_new = '%B %d %Y'

    headers = {
        'Authorization': 'Token {}'.format(api_key)
    }

    tags = input_tags.split(';')

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    params: Dict[str, Any] = {
        'number_of_posts': max_items
    }

    for tag in tags:
        root = ET.Element("root")
        if not (tag is None or tag == ''):
            params['tag'] = tag
            xml_filename = 'instagram_{}.xml'.format(tag)
            xml_temp_path = os.path.join(scala.temp_folder, xml_filename)
        else:
            params.pop('tag', None)
            xml_filename = 'instagram.xml'
            xml_temp_path = os.path.join(scala.temp_folder, xml_filename)

        scala.debug('file path temp: {}'.format(xml_temp_path))

        if check_too_old(xml_temp_path, max_file_age):

            response_json, is_error = request_json(URL, headers, params, False)

            if is_error:
                message = give_error_message(response_json)
                if response_json['type'] == 'ERROR':
                    scala.warn(message)
                elif response_json['type'] == 'WARN':
                    scala.warn(message)
                break
            else:
                response_json: Any

            for post in response_json:
                root.append(parse_post(post, max_characters,
                            scala.language, datetime_format_new))

            temp_path = scala.download_root_temp(root, xml_filename)
            scala.install_content(temp_path)
        else:
            scala.debug('File not old enough')


def check_api():
    svars = scala.variables

    tag = svars['tag']

    max_file_age = 60 * svars['max_minutes'] + 2

    scala.debug('max_file_age: {}'.format(max_file_age))

    if tag is '' or tag is None:
        svars['tag'] = ""
        file_name = 'instagram.xml'
    else:
        file_name = 'instagram_{}.xml'.format(tag)

    file_path = scala.find_content('Content://{}/{}'.format(NAME, file_name))

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

def get_media(post: Dict[str, Any]):
    return post.get('media', None)


def get_message(post: Dict[str, Any]):
    return post.get('message', '')


def get_creation_date(post: Dict[str, Any]):
    return post.get('created_at', '')[:19]


def get_likes(post: Dict[str, Any]):
    return post.get('likes', 0)


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################

def crop_message(text: str, max_length: int, language: int):
    if language == 1:
        append_text = "Lees verder op Instagram"
    else:
        append_text = "Read more on Instagram"

    if len(text) > max_length:
        return text[:max_length-3] + "...\n{}".format(append_text)
    else:
        return text


def parse_post(post: Dict[str, Any], max_characters: int, language_index: int, datetime_format_new: str):
    item = ET.Element("item")
    ET.SubElement(item, "likes").text = str(get_likes(post))
    ET.SubElement(item, "message").text = crop_message(
        remove_emoji(get_message(post)), max_characters, language_index)
    ET.SubElement(item, "created_time").text = parse_string_to_string(
        get_creation_date(post), DATETIME_FORMAT, datetime_format_new)

    thumbnail_url = get_media(post)
    if thumbnail_url is None:
        scala.debug('image not found so using placeholder')
        media_link = 'Content:\\placeholders\\img.png'
    else:
        temp_path = scala.download_media_temp(thumbnail_url)
        media_link = scala.install_content(temp_path)

    ET.SubElement(item, "media").text = media_link

    if media_link.endswith("mp4"):
        ET.SubElement(item, "media_type").text = "video"
    else:
        ET.SubElement(item, "media_type").text = "image"

    return item
