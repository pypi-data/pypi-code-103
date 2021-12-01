import os
import xml.etree.ElementTree as ET
from typing import Any, Dict

from firstimpression.api.request import give_error_message, request
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from requests.models import Response

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['news_polish']

BASE_URL = 'https://fi-api.io/news/interia/articles'

MAX_ITEMS = 4
MAX_FILE_AGE = 60 * 10

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    scala.debug('folder name: {}'.format(NAME))

    news_categories = scala.variables['news_categories'].strip(';').split(';')
    minimal_items = scala.variables['minimal_items']

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    minimal_items = MAX_ITEMS if minimal_items > MAX_ITEMS else minimal_items

    params: Dict[str, Any] = {
        'limit': MAX_ITEMS,
    }

    headers: Dict[str, str] = {
        'Authorization': 'Token {}'.format(scala.fi_api_key)
    }

    scala.debug('minimal_items: {}'.format(minimal_items))

    for news_category in news_categories:
        if news_category == '' or news_category is None:
            scala.warn('news category is empty')
            continue

        category = news_category.lower()

        xml_filename = '{}.xml'.format(category)

        xml_temp_path = os.path.join(
            scala.temp_folder, xml_filename)

        params['category'] = category

        scala.debug(
            'category: {} - temp path: {}'.format(category, xml_temp_path))

        if check_too_old(xml_temp_path, MAX_FILE_AGE):
            response = request(BASE_URL, headers, params)

            if not isinstance(response, Response):
                message = give_error_message(response)
                if response['type'] == 'ERROR':
                    scala.error(message)
                elif response['type'] == 'WARN':
                    scala.warn(message)

                raise SystemExit

            root = ET.fromstring(response.content)

            for image_original in root.iter('media'):
                if isinstance(image_original.text, str):
                    temp_path = scala.download_media_temp(image_original.text)
                    image_original.text = scala.install_content(
                        temp_path, category)
                    image_original.tag = 'image_original'

            for image_square in root.iter('media_sqr'):
                if isinstance(image_square.text, str):
                    temp_path = scala.download_media_temp(image_square.text)
                    image_square.text = scala.install_content(
                        temp_path, category)
                    image_square.tag = 'image_square'

            temp_path = scala.download_root_temp(root, xml_filename)
            scala.install_content(temp_path)


def check_api():
    svars = scala.variables
    news_categories = []

    if svars['polska']:
        news_categories.append('polska')

    if svars['sport']:
        news_categories.append('sport')

    if svars['kultura']:
        news_categories.append('kultura')

    for category in news_categories:
        if not category is None:
            scala.debug('category: {}'.format(category))
            file_path = scala.find_content(
                'Content://{}/{}.xml'.format(NAME, category))

            if check_too_old(file_path, MAX_FILE_AGE*2):
                svars['skipscript'] = True
                scala.debug('file too old')
                break
            else:
                svars['skipscript'] = False

                total_categories = len(news_categories)

                if total_categories == 0:
                    svars['skipscript'] = True
                    scala.warn('total_categories is empty')
                    break

##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################

##################################################################################################
# GET FUNCTIONS
##################################################################################################

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
