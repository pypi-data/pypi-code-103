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
from typing import Any

# 3rd Party Modules
import scrapy.settings

# Project Modules


DEFAULT_SETTINGS = {
    # General Settings
    'SCRACHY_REGION_NAME': None,
    'SCRACHY_FINGERPRINT_HASH_ALGORITHM': 'sha1',
    'SCRACHY_DIFF_TIMEOUT': 1.0,
    'SCRACHY_DEFAULT_ENCODING': 'utf-8',
    'SCRACHY_RESPONSE_RETRIEVAL_METHOD': 'standard',

    # Database Settings
    'SCRACHY_DIALECT': 'sqlite',
    'SCRACHY_DRIVER': None,
    'SCRACHY_HOST': None,
    'SCRACHY_PORT': None,
    'SCRACHY_DATABASE': None,
    'SCRACHY_SCHEMA': None,
    'SCRACHY_CREDENTIALS_FILE': None,

    # Content Extraction Settings
    'SCRACHY_USE_CONTENT_EXTRACTION': False,
    'SCRACHY_CONTENT_EXTRACTION_PARSER': 'html.parser',
    'SCRACHY_CONTENT_EXTRACTION_METHOD': 'basic',
    'SCRACHY_STORE_TEXT': False,

    # Simhash Settings
    'SCRACHY_USE_SIMHASH': False,
    'SCRACHY_SIMHASH_TOKENIZER': 'space',
    'SCRACHY_SIMHASH_KEEP_PUNCTUATION': False,
    'SCRACHY_SIMHASH_USE_LOWERCASE': True,
    'SCRACHY_SIMHASH_WINDOW': 4,
    'SCRACHY_SIMHASH_HASH_ALGORITHM': 'sha1',

    # Ignore Middleware Settings
    'SCRACHY_IGNORE_EXCLUDE_URL_PATTERNS': [],
}

VALID_HASH_ALGORITHMS = [
    'sha1', 'md5',                          # python hashlib
    'xxhash32', 'xxhash64', 'xxhash128',    # pip install xxhash
    'spooky32', 'spooky64', 'spooky128'     # pip install spookyhash
]
"""The names of the hash algorithms scrachy understands."""

VALID_DIALECTS = ['mssql', 'mysql', 'oracle', 'postgresql', 'sqlite']
"""The names of the database dialects scrachy understands."""

VALID_HTML_PARSERS = ['html5lib', 'lxml', 'lxml-xml', 'html.parser']
"""The names of the HTML parsers scrachy understands."""


VALID_CONTENT_EXTRACTION_METHODS = ['basic', 'boilerpipe_default', 'boilerpipe_article']
"""The names of the content extraction methods scrachy understands."""

VALID_TOKENIZERS = ['space', 'character', 'blingfire']
"""The names of the tokenizers scrachy understands."""

VALID_RESPONSE_RETRIEVAL_METHODS = ['standard', 'minimal', 'full']
"""The names of the response retrieval methods scrachy understands."""


def get_setting(name: str, settings: scrapy.settings.Settings, default_value: Any = None) -> Any:
    """
    Look up a scrachy setting or get it's default value.

    :param name: The name of the setting.
    :param settings: The project settings.
    :param default_value: Use this default value instead of the one from the DEFAULT_SETTINGS.
    :return: The value of the setting.
    """
    return settings.get(
        name,
        DEFAULT_SETTINGS.get(name) if default_value is None else default_value
    )
