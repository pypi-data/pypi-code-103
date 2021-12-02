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
import os

from typing import Tuple, Optional, Dict

# 3rd Party Modules
import scrapy
import scrapy.settings

# Project Modules
from scrachy.settings import DEFAULT_SETTINGS


def get_absolute_path(file_name: str) -> str:
    # Assume the file is in the same directory
    responses_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(responses_dir, file_name)


def read_file(file_name: str) -> str:
    file_path = get_absolute_path(file_name)

    with open(file_path, 'r') as fh:
        return fh.read()


def make_response_from_file(
        file_name: str,
        url: str,
        body: Optional[str] = None,
        meta: Optional[Dict[str, bool]] = None
) -> Tuple[scrapy.http.Request, scrapy.http.Response]:
    request = scrapy.http.Request(url=url, body=body, meta=meta or dict())
    file_content = read_file(file_name)

    response = scrapy.http.HtmlResponse(
        url=url,
        request=request,
        body=file_content,
        encoding='utf-8'
    )

    return request, response


def make_settings(
        region_name: str,
        database: Optional[str] = None,
        use_content_extraction: Optional[bool] = False,
        store_text: Optional[bool] = False,
        content_extraction_method: Optional[str] = 'basic',
        use_simhash: Optional[bool] = False,
) -> scrapy.settings.Settings:
    settings = scrapy.settings.Settings()

    for key, value in DEFAULT_SETTINGS.items():
        settings.set(key, value)

    settings.set('SCRACHY_DEFAULT_ENCODING', 'utf-8')
    settings.set('SCRACHY_REGION_NAME', region_name)
    settings.set('SCRACHY_DATABASE', database)
    settings.set('SCRACHY_USE_CONTENT_EXTRACTION', use_content_extraction)
    settings.set('SCRACHY_STORE_TEXT', store_text)
    settings.set('SCRACHY_CONTENT_EXTRACTION_METHOD', content_extraction_method)
    settings.set('SCRACHY_USE_SIMHASH', use_simhash)

    return settings
