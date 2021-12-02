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
import multiprocessing as mp
import os
import unittest

# 3rd Party Modules
import scrapy.crawler
import scrapy.utils.project

# Project Modules
from test.crawler.spider import BooksSpider


def delete_file(filename: str):
    # noinspection PyBroadException
    try:
        os.remove(filename)
    except Exception:
        pass


def run_spider(settings, stats: dict):
    process = scrapy.crawler.CrawlerProcess(settings)
    crawler = process.create_crawler(BooksSpider)

    process.crawl(crawler)
    process.start()

    stats['pages_scraped'] = crawler.spider.pages_scraped
    for key, value in crawler.stats.get_stats().items():
        stats[key] = value


class TestSpider(unittest.TestCase):
    def test_spider(self):
        settings = scrapy.utils.project.get_project_settings()
        database_file = settings.get('SCRACHY_DATABASE')

        # If the test failed or was aborted by the user, the database might
        # not have been deleted properly. So, make sure it's deleted here
        delete_file(database_file)

        with mp.Manager() as manager:
            result = manager.dict()
            p = mp.Process(target=run_spider, args=(settings, result,))
            p.start()
            p.join()

            initial_request_count = result['downloader/request_count']
            initial_response_count = result['downloader/response_count']
            initial_cache_miss = result.get('httpcache/miss', 0)
            initial_cache_store = result.get('httpcache/store', 0)
            initial_ignore_request = result.get(
                'downloader/exception_type_count/scrapy.exceptions.IgnoreRequest',
                0
            )

            result = manager.dict()
            p = mp.Process(target=run_spider, args=(settings, result,))
            p.start()
            p.join()

            second_request_count = result['downloader/request_count']
            second_response_count = result['downloader/response_count']
            second_cache_miss = result.get('httpcache/miss', 0)
            second_cache_store = result.get('httpcache/store', 0)
            second_ignore_request = result.get(
                'downloader/exception_type_count/scrapy.exceptions.IgnoreRequest',
                0
            )

            # I don't know if toscrape.com will ever add or remove pages, so I
            # don't want to assert against fixed numbers. Instead, I'll test
            # that the second time we scrape the page the critical statistics
            # are different. This isn't as robust a test as I'd like, but
            # combined with the offline tests it should be sufficient.
            self.assertGreater(initial_request_count, second_request_count)
            self.assertGreater(initial_response_count, second_response_count)
            self.assertGreater(initial_cache_miss, second_cache_miss)
            self.assertGreater(initial_cache_store, second_cache_store)
            self.assertLess(initial_ignore_request, second_ignore_request)
            self.assertEqual(initial_ignore_request, 0)

        delete_file(database_file)
