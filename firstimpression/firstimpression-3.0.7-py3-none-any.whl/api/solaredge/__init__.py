
import os
import xml.etree.ElementTree as ET

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

NAME = APIS['solaredge']
URL = 'https://monitoringpublic.solaredge.com/solaredge-web/p/kiosk/kioskData?locale=nl_NL'

XML_FILENAME = 'data.xml'

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

    guid = scala.variables['guid']

    scala.debug('folder name: {}'.format(NAME))
    scala.debug('guid: {}'.format(guid))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):

        root = ET.Element("root")

        response = request(URL, params={'guid': guid}, method='post')

        if not isinstance(response, Response):
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        response = response.text.split('\n')

        co2_saved = ''
        trees_saved = ''
        last_day_energy = ''

        for elem in response:
            if 'CO2EmissionSaved' in elem:
                co2_saved = '{:,}'.format(int(round(float(elem.split(':')[1].split(
                    ' ')[0][1:].replace('.', '').replace(',', '.')), 0))).replace(',', '.') + ' kg'
            if 'treesEquivalentSaved' in elem:
                trees_saved = '{:,}'.format(int(round(float(elem.split(
                    ':')[1][1:-3].replace('.', '').replace(',', '.')), 0))).replace(',', '.')
            if 'lastDayEnergy' in elem:
                last_day_energy = elem.split(':')[1][1:-3]

        ET.SubElement(root, "EmissionSaved").text = co2_saved
        ET.SubElement(root, "TreesSaved").text = trees_saved
        ET.SubElement(root, "EnergyToday").text = last_day_energy

        temp_path = scala.download_root_temp(root, XML_FILENAME)
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


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
