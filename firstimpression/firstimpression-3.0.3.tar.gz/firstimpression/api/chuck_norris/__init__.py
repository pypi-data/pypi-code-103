import json
import os
import random

from firstimpression.api.request import give_error_message, request_json
from firstimpression.constants import APIS
from firstimpression.file import (check_too_old, create_directories,
                                  purge_directories)
from firstimpression.placeholder import update_placeholders
from firstimpression.scala import ScalaPlayer

##################################################################################################
# CONSTANTS
##################################################################################################

PARAMS = {
    'firstName': 'firstname',
    'lastName': 'lastname',
    'exclude': ['explicit']
}

NAME = APIS['jokes']

JSON_FILENAME = 'jokes.json'

URL = 'http://api.icndb.com/jokes/'

MAX_FILE_AGE = 60 * 60 * 24

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

JSON_TEMP_PATH = os.path.join(scala.temp_folder, JSON_FILENAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def run_api():
    scala.debug('folder name: {}'.format(NAME))
    scala.debug('file path: {}'.format(JSON_TEMP_PATH))

    create_directories([scala.temp_folder, scala.content_folder])
    purge_directories([scala.temp_folder, scala.content_folder], max_days=1)
    update_placeholders()

    if check_too_old(JSON_TEMP_PATH, MAX_FILE_AGE):
        with open(JSON_TEMP_PATH, 'w') as file:
            response, is_error = request_json(URL, params=PARAMS)

            if is_error:
                message = give_error_message(response)
                if response['type'] == 'ERROR':
                    scala.error(message)
                elif response['type'] == 'WARN':
                    scala.warn(message)

                raise SystemExit

            response = response.get('value', None)
            if response is None:
                scala.warn('response is empty')
            else:
                scala.debug(response)
                json.dump(response, file)
        scala.install_content(JSON_TEMP_PATH)
    else:
        scala.debug('File not old enough to update')


def check_api():
    svars = scala.variables

    file_path = scala.find_content(
        'Content://{}/{}'.format(NAME, JSON_FILENAME))

    if check_too_old(file_path, MAX_FILE_AGE*2):
        svars['skipscript'] = True
        scala.debug('File to old to run chuck_norris')
    else:
        svars['skipscript'] = False
        svars['joke'] = get_random_joke(
            file_path, svars['firstname'], svars['lastname'])


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################

def get_random_joke(file_path: str, firstname: str, lastname: str):
    jokes = [elem['joke'] for elem in json.load(open(file_path, 'r'))]

    return random.SystemRandom().choice(jokes).replace(PARAMS['firstName'], firstname).replace(PARAMS['lastName'], lastname)

##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
