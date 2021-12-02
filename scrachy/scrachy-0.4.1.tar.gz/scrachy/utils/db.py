#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules
import logging
import urllib.parse

from typing import Dict

# 3rd Party Modules
import scrapy.settings

# Project Modules
from scrachy.settings import get_setting


log = logging.getLogger(__name__)


def load_credentials(settings: scrapy.settings.Settings) -> Dict[str, str]:
    """
    Load the database credentials from the specified file or return an empty
    dictionary if no file is specified.

    :param settings: The project settings.
    :return: A dictionary containing the user's credentials. The returned
             dictionary will have the keys {username, password} to access the
             corresponding values.
    """
    filename = get_setting('SCRACHY_CREDENTIALS_FILE', settings)

    credentials =  {
        'username': '',
        'password': ''
    }

    # If a credentials file was not specified, return an empty dict.
    if not filename:
        return credentials

    with open(filename, 'r') as fh:
        for line in fh:
            # Skip blank lines
            if not line.strip():
                continue

            key, value = line.split('=', 1)
            key, value = key.strip(), value.strip()

            value = urllib.parse.quote_plus(value) if key == 'password' else value

            credentials[key] = value

    return credentials


def make_database_url(settings: scrapy.settings.Settings) -> str:
    """
    Construct the url for connecting to the database.

    :return: The connection string.
    """
    dialect = get_setting('SCRACHY_DIALECT', settings)
    driver = get_setting('SCRACHY_DRIVER', settings)
    credentials = load_credentials(settings)
    username = credentials['username']
    password = credentials['password']
    host = get_setting('SCRACHY_HOST', settings)
    port = get_setting('SCRACHY_PORT', settings)
    database = get_setting('SCRACHY_DATABASE', settings)

    url = dialect

    if driver:
        url += f"+{driver}"

    url += "://"

    if username and password:
        url += f"{username}:{password}@"
    elif username:
        url += f"{username}@"
    elif password:
        log.warning(
            "Trying to connect to the cache using a password without a username. "
            "The password will be ignored."
        )

    if host:
        url += host

    if port:
        url += f":{port}"

    url += f"/{database if database else ''}"

    return url
