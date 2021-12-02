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
import datetime

from typing import Optional

# 3rd Party Modules
import scrapy

# Project Modules


class CachedHtmlResponse(scrapy.http.HtmlResponse):
    def __init__(
            self,
            scrape_timestamp: Optional[datetime.datetime] = None,
            content_extraction_method: Optional[str] = None,
            content_extraction_parser: Optional[str] = None,
            simhash_hash_algorithm: Optional[str] = None,
            html_number_of_bytes: Optional[int] = None,
            text_number_of_bytes: Optional[int] = None,
            body_text: Optional[str] = None,
            simhash_value: Optional[int] = None,
            *args,
            **kwargs
    ):
        """
        A subclass of :class:`scrapy.http.HttpResponse` that contains a
        subset of the extra information stored in the cache.

        :param scrape_timestamp: The most recent date the request was scraped.
        :param content_extraction_method: The name of the method used to
               extract the textual content from the html.
        :param content_extraction_parser: The HTML parser used to extract
               the content.
        :param simhash_hash_algorithm: The hash algorithm used to create the
               simhash value.
        :param html_number_of_bytes: The total number of bytes of the downloaded
               html.
        :param text_number_of_bytes: The number of bytes in the extracted
               plain text.
        :param body_text: The text extracted from the HTML.
        :param simhash_value: The value of the simhash computation.
        """
        super().__init__(*args, **kwargs)

        self.scrape_timestamp = scrape_timestamp
        self.content_extraction_method = content_extraction_method
        self.content_extraction_parser = content_extraction_parser
        self.simhash_hash_algorithm = simhash_hash_algorithm
        self.html_number_of_bytes = html_number_of_bytes
        self.text_number_of_bytes = text_number_of_bytes
        self.body_text = body_text
        self.simhash = simhash_value
