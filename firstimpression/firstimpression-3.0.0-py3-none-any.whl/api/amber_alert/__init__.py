import xml.etree.ElementTree as ET
import os

from requests.models import Response

from firstimpression.constants import APIS
from firstimpression.file import check_too_old, create_directories, purge_directories
from firstimpression.scala import ScalaPlayer
from firstimpression.placeholder import update_placeholders
from firstimpression.api.request import give_error_message, request
from firstimpression.xml import path_to_root

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['amber']

XML_FILENAME = 'amber_alert.xml'

URL = 'https://media.amberalert.nl/xml/combined/index.xml'

URL_LOGO = 'https://fi-digital-signage.s3.eu-central-1.amazonaws.com/amber_alert/logo.png'

MAX_FILE_AGE = 60 * 10

NAMESPACE_XML = {
    'NP': 'http://www.netpresenter.com'
}

TAGS = {
    'alert': 'NP:Alert',
    'soort': 'NP:AlertLevel',
    'status': 'NP:Status',
    'type': 'NP:Type',
    'message': 'NP:Message/NP:Common/NP:ISource',
    'name': 'NP:Title',
    'description': 'NP:Description',
    'readmore': 'NP:Readmore_URL',
    'amberlink': 'NP:Media_URL',
    'image': 'NP:Media/NP:Image'
}

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
    scala.debug(
        'File locations: temp -> {} & local -> {}'.format(scala.temp_folder, scala.content_folder))

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

        counter = 0

        temp_path = scala.download_media_temp(URL_LOGO)
        scala.install_content(temp_path)

        for alert in get_alerts(root):
            counter += 1
            new_root.append(parse_alert(alert))

        ET.SubElement(new_root, "alerts").text = str(counter)

        if counter == 0:
            scala.debug('No alerts to show')

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

        total_items = int(path_to_root(file_path).get('alerts', '0'))

        if total_items == 0:
            svars['skipscript'] = True
            scala.debug('No alerts to show')


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


def download_photo_child(url: str):
    temp_path = scala.download_media_temp(url)
    return scala.install_content(temp_path)

##################################################################################################
# GET FUNCTIONS
##################################################################################################


def get_alerts(root: ET.Element):
    return root.findall(TAGS['alert'], NAMESPACE_XML)


def get_alert_soort(alert: ET.Element):
    if alert.findtext(TAGS['soort'], '0', NAMESPACE_XML) == '10':
        return 'Amber Alert'
    else:
        return 'Vermist kind'


def get_alert_status(alert: ET.Element):
    return alert.findtext(TAGS['status'], 'Onbekend', NAMESPACE_XML)


def get_alert_type(alert: ET.Element):
    return alert.findtext(TAGS['type'], 'Onbekend', NAMESPACE_XML)


def get_alert_message(alert: ET.Element):
    return alert.find(TAGS['message'], NAMESPACE_XML)


def get_name_child(message: ET.Element):
    return message.findtext(TAGS['name'], 'Onbekend', NAMESPACE_XML)


def get_message_description(message: ET.Element):
    return message.findtext(TAGS['description'], '', NAMESPACE_XML)


def get_more_info_url(message: ET.Element):
    return message.findtext(TAGS['readmore'], '', NAMESPACE_XML)


def get_amber_url(message: ET.Element):
    return message.findtext(TAGS['amberlink'], '', NAMESPACE_XML)


def get_photo_child(message: ET.Element):
    media_url = message.findtext(TAGS['image'], None, NAMESPACE_XML)

    if media_url is None:
        return 'Content:\\placeholders\\img.png'
    else:
        return download_photo_child(media_url)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################


def parse_alert(alert: ET.Element):
    item = ET.Element("item")
    ET.SubElement(item, "soort").text = get_alert_soort(alert)
    ET.SubElement(item, "status").text = get_alert_status(alert)
    ET.SubElement(item, "type").text = get_alert_type(alert)

    message = get_alert_message(alert)

    if message is None:
        return item

    ET.SubElement(item, "naam").text = get_name_child(message)
    ET.SubElement(item, "description").text = get_message_description(message)
    ET.SubElement(item, "readmore").text = get_more_info_url(message)
    ET.SubElement(item, "amberlink").text = get_amber_url(message)
    ET.SubElement(item, "image").text = get_photo_child(message)

    return item
