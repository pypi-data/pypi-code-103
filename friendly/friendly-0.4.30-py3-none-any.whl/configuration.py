"Configuration file exclusively for friendly -- not for friendly-traceback"

import configparser
import os

from friendly_traceback import debug_helper

FILENAME = os.path.join(os.path.expanduser("~"), ".friendly.ini")

def read(section="friendly", value=None):
    if not os.path.exists(FILENAME):
        return None
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if section in config and value in config[section]:
        return config[section][value]
    return None


def write(section="friendly", value=None):
    if value is None or section is None:
        debug_helper.log("Attempting to write None in configuration.py")
        return
    if not os.path.exists(FILENAME):
        return
    config = configparser.ConfigParser()
    config.read(FILENAME)
