from firstimpression.api.request import give_error_message, request
from firstimpression.placeholder import update_placeholders
import os
import xml.etree.ElementTree as ET
from requests.models import Response

from firstimpression.constants import APIS
from firstimpression.file import check_too_old, create_directories, purge_directories
from firstimpression.scala import ScalaPlayer

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['trends']

XML_FILENAME = 'trends.xml'

URL = 'https://trends.google.nl/trends/hottrends/atom/feed?pn=p17'

NAMESPACE = {
    'atom': 'http://www.w3.org/2005/Atom',
    'ht': 'https://trends.google.nl/trends/trendingsearches/daily'
}

TAGS = {
    'item': 'channel/item',
    'title': 'title',
    'traffic': 'ht:approx_traffic',
    'url': 'link'
}

MAX_FILE_AGE = 60 * 30

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

XML_TEMP_PATH = os.path.join(scala.temp_folder, XML_FILENAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():

    scala.debug('folder name: {}'.format(NAME))
    scala.debug('file location temp: {}'.format(XML_TEMP_PATH))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        response = request(URL)

        if not isinstance(response, Response):
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        root = ET.fromstring(response.content)
        new_root = ET.Element("root")

        for elem in root.findall(TAGS['item']):
            item = ET.SubElement(new_root, "item")
            ET.SubElement(item, "title").text = get_title(elem)
            ET.SubElement(item, "traffic").text = str(get_traffic(elem))
            ET.SubElement(item, "url").text = get_url(elem)

        scala.debug(str(new_root))

        temp_path = scala.download_root_temp(new_root, XML_FILENAME)
        scala.install_content(temp_path)
    else:
        scala.debug('File not old enough to update')


def check_api():
    svars = scala.variables

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, XML_FILENAME))

    if check_too_old(file_path, MAX_FILE_AGE*2):
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

def get_title(elem: ET.Element):
    return elem.findtext(TAGS['title'], '')


def get_traffic(elem: ET.Element):
    return elem.findtext(TAGS['traffic'], '', NAMESPACE)


def get_url(elem: ET.Element):
    return elem.findtext(TAGS['url'], '')

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
