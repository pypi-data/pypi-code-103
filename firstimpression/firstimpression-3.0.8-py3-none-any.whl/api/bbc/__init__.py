import os
import xml.etree.ElementTree as ET

from firstimpression.api.request import give_error_message, request
from firstimpression.constants import APIS, REPLACE_DICT, TAGS_TO_REMOVE
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from firstimpression.text import remove_tags_from_string, replace_html_entities
from firstimpression.time import parse_string_to_string
from firstimpression.xml import path_to_root
from requests.models import Response

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['bbc']

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
DATETIME_ABREVIATION_FORMAT = '%b %d %Y %H:%M'
DATETIME_FULL_FORMAT = '%B %d %Y %H:%M'

MAX_ITEMS = 10
MAX_FILE_AGE = 60 * 10

TAGS = {
    'item': 'channel/item',
    'title': 'title',
    'descr': 'description',
    'pubDate': 'pubDate'
}

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    scala.debug('folder name: {}'.format(NAME))

    news_category = scala.variables['news_category']
    minimal_items = scala.variables['minimal_items']

    xml_file_name = '{}.xml'.format(news_category)
    xml_temp_path = os.path.join(scala.temp_folder, xml_file_name)

    scala.debug('file path {}: {}'.format(news_category, xml_temp_path))

    url = 'http://feeds.bbci.co.uk/news/{}/rss.xml'.format(news_category)
    minimal_items = MAX_ITEMS if minimal_items > MAX_ITEMS else minimal_items

    scala.debug('url: {}'.format(url))
    scala.debug('minimal_items: {}'.format(minimal_items))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()
    scala.set_language('EN')

    if check_too_old(xml_temp_path, MAX_FILE_AGE):
        root = ET.Element("root")
        response = request(url)

        if not isinstance(response, Response):
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        feed = ET.fromstring(response.content)

        for news_item in get_news_items(feed):
            root.append(parse_news_item(news_item))

            if len(root) == MAX_ITEMS:
                scala.debug('max amount of items reached')
                break

        if len(root) >= minimal_items:
            temp_path = scala.download_root_temp(root, xml_file_name)
            scala.install_content(temp_path)
        else:
            scala.warn('root consist out of less than minimal items.')
    else:
        scala.debug('file not old enough to update')


def check_api():
    svars = scala.variables

    file_path = scala.find_content(
        'Content://{}/{}.xml'.format(NAME, svars['news_category']))

    if check_too_old(file_path, MAX_FILE_AGE*2):
        svars['skipscript'] = True
        scala.debug('file too old')
    else:
        svars['skipscript'] = False

        total_items = len(path_to_root(file_path))

        if total_items == 0:
            svars['skipscript'] = True
            scala.warn('No items found in xml file')


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_news_items(root: ET.Element):
    return root.findall(TAGS['item'])


def get_news_title(news_item: ET.Element):
    return replace_html_entities(REPLACE_DICT, news_item.findtext(TAGS['title'], ''))


def get_news_description(news_item: ET.Element):
    return remove_tags_from_string(TAGS_TO_REMOVE, news_item.findtext(TAGS['descr'], ''))


def get_short_date(news_item: ET.Element):
    return parse_string_to_string(news_item.findtext(TAGS['pubDate'], ''), DATETIME_FORMAT, DATETIME_ABREVIATION_FORMAT)


def get_full_date(news_item: ET.Element):
    return parse_string_to_string(news_item.findtext(TAGS['pubDate'], ''), DATETIME_FORMAT, DATETIME_FULL_FORMAT)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_news_item(news_item: ET.Element):
    item = ET.Element("item")
    ET.SubElement(item, "title").text = get_news_title(news_item)
    ET.SubElement(item, "descr").text = get_news_description(news_item)
    ET.SubElement(item, "pubDate").text = get_short_date(news_item)
    ET.SubElement(item, "fullMonthPubDate").text = get_full_date(news_item)

    scala.debug('item: {}'.format(item))

    return item
