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
import tempfile
import time
import unittest

# 3rd Party Modules
import scrapy.exceptions

# Project Modules
from scrachy.middleware.httpcache import AlchemyCacheStorage
from scrachy.middleware.ignorecached import IgnoreCachedResponse
from test.utils import make_response_from_file, make_settings


class TestIgnoreCachedResponse(unittest.TestCase):
    settings = None
    storage_file = None
    storage = None

    requests = []
    responses = []

    @classmethod
    def setUpClass(cls) -> None:
        filename1, url1 = 'test_page_1.html', 'http://www.example1.com/'
        filename2, url2 = 'test_page_2.html', 'http://www.example2.com/'
        filename3, url3 = 'test_page_3.html', 'http://www.acme1.com/'
        filename4, url4 = 'test_page_3.html', 'http://www.acme2.com/'

        cls.storage_file = tempfile.NamedTemporaryFile()
        cls.settings = make_settings('test_ignore_cache', database=cls.storage_file.name)
        cls.settings.set('SCRACHY_IGNORE_EXCLUDE_URL_PATTERNS', [r'www\.acme\d+.com'])
        cls.settings.set('HTTPCACHE_EXPIRATION_SECS', 0)
        cls.storage = AlchemyCacheStorage(cls.settings)
        cls.storage.open_spider(None)

        # We'll store several request/responses in the cache
        pairs = [
            make_response_from_file(filename1, url1),
            make_response_from_file(filename2, url2, meta={'dont_cache': True}),
            make_response_from_file(filename2, url2, '{param=value}', meta={'dont_ignore': True}),
            make_response_from_file(filename3, url3),
            make_response_from_file(filename4, url4)
        ]
        cls.requests = requests = [p[0] for p in pairs]
        cls.responses = responses = [p[1] for p in pairs]

        for request, response in zip(requests, responses):
            cls.storage.store_response(None, request, response)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.storage_file:
            cls.storage_file.close()

    def test_should_ignore(self):
        middleware = IgnoreCachedResponse(self.settings)

        with self.assertRaises(scrapy.exceptions.IgnoreRequest):
            middleware.process_request(self.requests[0], None)

        for request in self.requests[1:]:
            try:
                middleware.process_request(request, None)
            except scrapy.exceptions.IgnoreRequest:
                self.fail(f"This request should not be ignored: {request} {request.meta}")

    def test_exclude_if_expired(self):
        time.sleep(0.2)
        settings = self.settings.copy()
        settings.set('HTTPCACHE_EXPIRATION_SECS', 0.1)

        middleware = IgnoreCachedResponse(settings)

        # All requests should be ignored in this case
        for request in self.requests:
            try:
                middleware.process_request(request, None)
            except scrapy.exceptions.IgnoreRequest:
                self.fail(f"This request should not be ignored: {request} {request.meta}")


if __name__ == '__main__':
    unittest.main()
