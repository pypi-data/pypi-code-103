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
import re

# 3rd Party Modules
import scrapy

# Project Modules


log = logging.getLogger(__name__)


class BooksSpider(scrapy.spiders.Spider):
    """
    A sample spider similar to the
    [scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html).
    """
    name = 'books'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pages_scraped = 0

    def start_requests(self):
        urls = ['http://books.toscrape.com/index.html']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'dont_ignore': True})

    def parse(self, response: scrapy.http.Response, **kwargs):
        """
        Simply follow all links on the page.

        :param response:
        :param kwargs:
        :return:
        """
        self.pages_scraped += 1

        links = response.css('a::attr(href)')

        for link in links:
            page_num = 0
            page_matcher = re.search(r'page-(\d+)', link.extract())
            if page_matcher:
                page_num = int(page_matcher.group(1))

            # Only follow the first 2 pages
            if page_num < 2:
                yield response.follow(link, callback=self.parse)
