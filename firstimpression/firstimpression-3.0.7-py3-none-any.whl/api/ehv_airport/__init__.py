import os
import xml.etree.ElementTree as ET

import lxml.html
from firstimpression.api.request import give_error_message, request
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer
from requests import Response

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['eindhoven']
URL = 'https://www.eindhovenairport.nl/nl/vertrektijden'

XML_FILENAME = 'flights.xml'
MAX_FILE_AGE = 60 * 10

TABLE_FLIGHTS_XPATH = '//div[@id="skyguide"]/div/table'

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
    scala.debug('temp path: {}'.format(XML_TEMP_PATH))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        root = ET.Element("root")

        response = request(URL)

        if not isinstance(response, Response):
            message = give_error_message(response)
            if response['type'] == 'ERROR':
                scala.error(message)
            elif response['type'] == 'WARN':
                scala.warn(message)

            raise SystemExit

        response = lxml.html.fromstring(response.text)

        table = response.xpath(TABLE_FLIGHTS_XPATH)[0]

        for row in table.xpath('tr'):
            item = ET.Element("item")
            store = False
            column_number = 1

            for column in row.xpath('td'):
                column_text = column.xpath('text()')

                if len(column_text) == 0:
                    column_text.append('')

                if column_number == 1:
                    ET.SubElement(item, "departure_time").text = column_text[0]
                elif column_number == 2:
                    ET.SubElement(item, "flight_number").text = column_text[0]
                elif column_number == 3:
                    ET.SubElement(item, "route").text = column_text[0]
                elif column_number == 4:
                    ET.SubElement(item, "status").text = column_text[0]
                    if not "Vertrokken" in column_text[0]:
                        scala.debug('flight {} already left'.format(
                            item.findtext('flight_number')))
                        store = True
                elif column_number == 5:
                    pass

                column_number += 1

            if store:
                root.append(item)

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
