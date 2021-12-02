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

# Python modules
import datetime
import logging
import tempfile
import time
import unittest

from typing import Set, cast

# 3rd Party modules
import scrapy.settings


# Project modules
from scrachy.exceptions import InvalidSettingError
from scrachy.http import CachedHtmlResponse
from scrachy.middleware import httpcache
from scrachy.middleware.httpcache import AlchemyCacheStorage
from scrachy.settings import VALID_HASH_ALGORITHMS, VALID_DIALECTS, VALID_HTML_PARSERS, \
    VALID_CONTENT_EXTRACTION_METHODS, VALID_TOKENIZERS
from scrachy.utils.db import make_database_url


from test.utils import get_absolute_path, make_response_from_file, make_settings, read_file

# Optional modules
try:
    import blingfire
except ImportError:
    blingfire = None

try:
    import boilerpy3 as bp3
except ImportError:
    bp3 = None

try:
    import xxhash
except ImportError:
    xxhash = None


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)-15s [%(name)s]:%(lineno)d %(levelname)s %(message)s'
)


log = logging.getLogger('test_rdb_cache_storage')


# These should match the class and database property names that correspond
# to the scrachy setting names. If these properties or database column names
# change these need to be updated to match them exactly.
# The values should be different than the default values for each key.
non_default_settings = {
    'body_hash_algorithm': 'md5',
    'use_simhash': True,
    'simhash_tokenizer': 'character',
    'simhash_window': 3,
    'simhash_keep_punctuation': True,
    'simhash_use_lowercase': False,
    'simhash_hash_algorithm': 'md5',
    'content_extraction_parser': 'lxml',
    'content_extraction_method': 'boilerpipe_default',
    'response_retrieval_method': 'full'
}


class TestAlchemyCacheStorage(unittest.TestCase):
    region_name = 'test_cache'

    def tearDown(self) -> None:
        AlchemyCacheStorage.clear_cache()

    def test_settings(self):
        settings = make_settings(self.region_name)
        storage = AlchemyCacheStorage(settings)

        try:
            storage.open_spider(None)
        except InvalidSettingError as e:
            self.fail(f"Settings are not valid: {e}")

        settings.set('SCRACHY_UNKNOWN_SETTING', True)

        with self.assertRaises(InvalidSettingError):
            storage.validate_and_assign_settings()

        self._test_options('SCRACHY_FINGERPRINT_HASH_ALGORITHM', settings, VALID_HASH_ALGORITHMS)
        self._test_options('SCRACHY_SIMHASH_HASH_ALGORITHM', settings, VALID_HASH_ALGORITHMS)
        self._test_options('SCRACHY_CONTENT_EXTRACTION_PARSER', settings, VALID_HTML_PARSERS)
        self._test_options('SCRACHY_CONTENT_EXTRACTION_METHOD', settings, VALID_CONTENT_EXTRACTION_METHODS)
        self._test_options('SCRACHY_SIMHASH_TOKENIZER', settings, VALID_TOKENIZERS)

        # This needs to be done slightly differently because invalid dialects do
        # not raise exceptions.
        # Check the valid dialects do not raise exceptions
        current_dialect = settings.get('SCRACHY_DIALECT')
        for dialect in VALID_DIALECTS:
            settings.set('SCRACHY_DIALECT', dialect)

            try:
                AlchemyCacheStorage(settings)._validate_supported_options()
            except InvalidSettingError:
                self.fail("A valid dialect was flagged as invalid.")

        # Check an invalid dialect logs a warning
        with self.assertLogs('scrachy.middleware.httpcache', level='WARNING') as log_ctx:
            settings.set('SCRACHY_DIALECT', 'unk_dialect')
            AlchemyCacheStorage(settings)._validate_supported_options()
        self.assertTrue("Unsupported database dialect" in log_ctx.output[0])
        settings.set('SCRACHY_DIALECT', current_dialect)

    def test_make_sqlite_url(self):
        settings = make_settings(self.region_name)

        settings.set('SCRACHY_DIALECT', 'sqlite')

        # In memory
        act_url = make_database_url(settings)
        exp_url = 'sqlite:///'

        self.assertEqual(act_url, exp_url)

        # Using Pysqlite driver
        settings.set('SCRACHY_DRIVER', 'pysqlite')

        act_url = make_database_url(settings)
        exp_url = 'sqlite+pysqlite:///'

        self.assertEqual(act_url, exp_url)

        # Test relative path name
        settings.set('SCRACHY_DATABASE', 'relative_path/to/file.db')

        act_url = make_database_url(settings)
        exp_url = 'sqlite+pysqlite:///relative_path/to/file.db'

        self.assertEqual(act_url, exp_url)

        # Test absolute path name
        settings.set('SCRACHY_DATABASE', '/absolute_path/to/file.db')

        act_url = make_database_url(settings)
        exp_url = 'sqlite+pysqlite:////absolute_path/to/file.db'

        self.assertEqual(act_url, exp_url)

    def test_make_other_db_url(self):
        settings = make_settings(self.region_name)
        settings.set('SCRACHY_DIALECT', 'mysql')
        settings.set('SCRACHY_HOST', 'localhost')

        storage = AlchemyCacheStorage(settings)

        # Test to make sure an error is raised if a database is not specified
        # with a dialect other than sqlite
        with self.assertRaises(InvalidSettingError):
            storage._validate_database_parameters()

        # Add a database
        settings.set('SCRACHY_DATABASE', 'mydb')

        act_url = make_database_url(settings)
        exp_url = 'mysql://localhost/mydb'

        self.assertEqual(act_url, exp_url)

        # Add a username and password
        credentials_file_path = get_absolute_path('credentials1.txt')
        settings.set('SCRACHY_CREDENTIALS_FILE', credentials_file_path)

        act_url = make_database_url(settings)
        exp_url = 'mysql://user1:pass1@localhost/mydb'

        self.assertEqual(act_url, exp_url)

        # Set a password that needs to be url encoded
        credentials_file_path = get_absolute_path('credentials2.txt')
        settings.set('SCRACHY_CREDENTIALS_FILE', credentials_file_path)

        act_url = make_database_url(settings)
        exp_url = 'mysql://user2:kx%25jj5%2Fg@localhost/mydb'

        self.assertEqual(act_url, exp_url)

        # Set a username without a password
        credentials_file_path = get_absolute_path('credentials3.txt')
        settings.set('SCRACHY_CREDENTIALS_FILE', credentials_file_path)

        act_url = make_database_url(settings)
        exp_url = 'mysql://user3@localhost/mydb'

        self.assertEqual(act_url, exp_url)

        # Set a password without a user
        credentials_file_path = get_absolute_path('credentials4.txt')
        settings.set('SCRACHY_CREDENTIALS_FILE', credentials_file_path)

        act_url = make_database_url(settings)
        exp_url = 'mysql://localhost/mydb'

        self.assertEqual(act_url, exp_url)

    def test_open_spider_same_settings(self):
        settings = make_settings(self.region_name)

        with tempfile.NamedTemporaryFile() as tf:
            settings.set('SCRACHY_DATABASE', tf.name)

            storage = AlchemyCacheStorage(settings)

            # The default settings should work
            # noinspection PyBroadException
            try:
                storage.open_spider(None)
            except Exception as e:
                self.fail(f"An unexpected exception occurred: {e}")
            finally:
                storage.clear_cache()

    def test_open_spider_different_fingerprint(self):
        settings = make_settings(self.region_name)
        with tempfile.NamedTemporaryFile() as tf:
            settings.set('SCRACHY_DATABASE', tf.name)

            storage = AlchemyCacheStorage(settings)

            # noinspection PyBroadException
            try:
                storage.open_spider(None)
            except Exception as e:
                self.fail(f"An unexpected exception occurred: {e}")
            finally:
                storage.clear_cache()

            # Changing the fingerprint hash algorithm should always raise an
            # exception
            with self.assertRaises(InvalidSettingError):
                settings.set('SCRACHY_FINGERPRINT_HASH_ALGORITHM', 'md5')
                storage = AlchemyCacheStorage(settings)
                storage.open_spider(None)

    def test_store_response_no_duplicates(self):
        filename1, url1 = 'test_page_1.html', 'http://www.example1.com/'
        filename2, url2 = 'test_page_2.html', 'http://www.example2.com/'
        filename3, url3 = 'test_page_2.html', 'http://www.example3.com/'

        # We'll store three request/responses in the cache
        request1, response1 = make_response_from_file(filename1, url1)
        request2, response2 = make_response_from_file(filename2, url2)
        request3, response3 = make_response_from_file(filename2, url2, '{param=value}')
        request4, response4 = make_response_from_file(filename3, url3, '{param=value}')

        settings = make_settings(self.region_name)

        with tempfile.NamedTemporaryFile() as tf:
            # Test without text
            settings.set('SCRACHY_DATABASE', tf.name)
            storage = AlchemyCacheStorage(settings)
            storage.open_spider(None)
            storage.store_response(None, request1, response1)

            items = storage.dump_cache()

            self.assertEqual(len(items), 1)

            item = items[0]

            # I suppose this could fail if the test was run right before midnight :-/
            self.assertEqual(item.region_name, 'test_cache')
            self.assertEqual(item.scrape_timestamp.date(), datetime.date.today())
            self.assertEqual(item.request_fingerprint.hex(), '6f46785fc46898dfd4675d6cb9b2c32e22a024b9')
            self.assertEqual(item.request_url, url1)
            self.assertEqual(item.request_netloc, 'www.example1.com')
            self.assertEqual(item.request_method, 'GET')
            self.assertEqual(item.request_body, b'')
            self.assertEqual(item.response_status, 200)
            self.assertEqual(item.response_headers, '')
            self.assertEqual(item.response_body_html, response1.text)
            self.assertEqual(item.response_body_text, None)
            self.assertEqual(item.response_body_html_number_of_bytes, 625)
            self.assertIsNone(item.response_body_text_number_of_bytes)
            self.assertEqual(item.response_body_text_simhash, None)

            # Test store text if extract content is True
            settings.set('SCRACHY_USE_CONTENT_EXTRACTION', True)
            settings.set('SCRACHY_STORE_TEXT', True)
            storage = AlchemyCacheStorage(settings)
            storage.open_spider(None)
            storage.store_response(None, request2, response2)

            items = storage.dump_cache()

            self.assertEqual(len(items), 2)

            item = items[1]

            self.assertIsNotNone(item.response_body_text)

            # Test that the same url with a different request body generates a
            # different hash (even if the contents are the same).
            storage.store_response(None, request3, response3)

            items = storage.dump_cache()
            self.assertEqual(len(items), 3)
            self.assertNotEqual(items[2].request_fingerprint, items[1].request_fingerprint)
            storage.close_spider(None)

            # Test store text if extract content is False
            settings.set('SCRACHY_USE_CONTENT_EXTRACTION', False)
            settings.set('SCRACHY_STORE_TEXT', True)
            storage = AlchemyCacheStorage(settings)

            storage.open_spider(None)
            with self.assertLogs('scrachy.middleware.httpcache', level='WARNING') as log_ctx:
                storage.open_spider(None)

            self.assertTrue(
                "SCRACHY_STORE_TEXT is True, but SCRACHY_USE_CONTENT_EXTRACTION is False"
                in log_ctx.output[0]
            )
            storage.store_response(None, request4, response4)
            items = storage.dump_cache()
            item = items[-1]
            self.assertEqual(item.response_body_text, None)

    # Simhash
    def test_tokenization_and_punctuation(self):
        text = (
            "\"We saw the amazing community that’s grown up around Kubernetes, and we wanted to "
            "be part of that. We …\"\nCopyright © 2019 The Linux Foundation ®. All rights reserved."
        )

        # Test tokenizers and punctuation
        # Always test these
        # space
        act_tokens = httpcache.space_tokenizer(text)
        exp_tokens = [
            '"We', 'saw', 'the', 'amazing', 'community', 'that’s', 'grown', 'up', 'around',
            'Kubernetes,', 'and', 'we', 'wanted', 'to', 'be', 'part', 'of', 'that.', 'We', '…"',
            'Copyright', '©', '2019', 'The', 'Linux', 'Foundation', '®.', 'All', 'rights',
            'reserved.']
        self.assertEqual(act_tokens, exp_tokens)

        # Should be an identity function
        act_tokens = AlchemyCacheStorage.normalize_punctuation(act_tokens, True)
        self.assertEqual(act_tokens, exp_tokens)

        act_tokens = AlchemyCacheStorage.normalize_punctuation(act_tokens, False)
        exp_tokens = [
            'We', 'saw', 'the', 'amazing', 'community', 'that’s', 'grown', 'up', 'around',
            'Kubernetes', 'and', 'we', 'wanted', 'to', 'be', 'part', 'of', 'that', 'We', '…',
            'Copyright', '©', '2019', 'The', 'Linux', 'Foundation', '®', 'All', 'rights',
            'reserved']
        self.assertEqual(act_tokens, exp_tokens)

        # character
        act_tokens = httpcache.character_tokenizer(text)
        exp_tokens = [
            '"', 'W', 'e', ' ', 's', 'a', 'w', ' ', 't', 'h', 'e', ' ', 'a', 'm', 'a', 'z', 'i',
            'n', 'g', ' ', 'c', 'o', 'm', 'm', 'u', 'n', 'i', 't', 'y', ' ', 't', 'h', 'a', 't',
            '’', 's', ' ', 'g', 'r', 'o', 'w', 'n', ' ', 'u', 'p', ' ', 'a', 'r', 'o', 'u', 'n',
            'd', ' ', 'K', 'u', 'b', 'e', 'r', 'n', 'e', 't', 'e', 's', ',', ' ', 'a', 'n', 'd',
            ' ', 'w', 'e', ' ', 'w', 'a', 'n', 't', 'e', 'd', ' ', 't', 'o', ' ', 'b', 'e', ' ',
            'p', 'a', 'r', 't', ' ', 'o', 'f', ' ', 't', 'h', 'a', 't', '.', ' ', 'W', 'e', ' ',
            '…', '"', '\n', 'C', 'o', 'p', 'y', 'r', 'i', 'g', 'h', 't', ' ', '©', ' ', '2', '0',
            '1', '9', ' ', 'T', 'h', 'e', ' ', 'L', 'i', 'n', 'u', 'x', ' ', 'F', 'o', 'u', 'n',
            'd', 'a', 't', 'i', 'o', 'n', ' ', '®', '.', ' ', 'A', 'l', 'l', ' ', 'r', 'i', 'g',
            'h', 't', 's', ' ', 'r', 'e', 's', 'e', 'r', 'v', 'e', 'd', '.']
        self.assertEqual(act_tokens, exp_tokens)

        act_tokens = AlchemyCacheStorage.normalize_punctuation(act_tokens, False)
        exp_tokens = [
            'W', 'e', ' ', 's', 'a', 'w', ' ', 't', 'h', 'e', ' ', 'a', 'm', 'a', 'z', 'i', 'n',
            'g', ' ', 'c', 'o', 'm', 'm', 'u', 'n', 'i', 't', 'y', ' ', 't', 'h', 'a', 't', '’',
            's', ' ', 'g', 'r', 'o', 'w', 'n', ' ', 'u', 'p', ' ', 'a', 'r', 'o', 'u', 'n', 'd',
            ' ', 'K', 'u', 'b', 'e', 'r', 'n', 'e', 't', 'e', 's', ' ', 'a', 'n', 'd', ' ', 'w',
            'e', ' ', 'w', 'a', 'n', 't', 'e', 'd', ' ', 't', 'o', ' ', 'b', 'e', ' ', 'p', 'a',
            'r', 't', ' ', 'o', 'f', ' ', 't', 'h', 'a', 't', ' ', 'W', 'e', ' ', '…', '\n', 'C',
            'o', 'p', 'y', 'r', 'i', 'g', 'h', 't', ' ', '©', ' ', '2', '0', '1', '9', ' ', 'T',
            'h', 'e', ' ', 'L', 'i', 'n', 'u', 'x', ' ', 'F', 'o', 'u', 'n', 'd', 'a', 't', 'i',
            'o', 'n', ' ', '®', ' ', 'A', 'l', 'l', ' ', 'r', 'i', 'g', 'h', 't', 's', ' ', 'r',
            'e', 's', 'e', 'r', 'v', 'e', 'd']
        self.assertEqual(act_tokens, exp_tokens)

        # Conditionally test the following (if they are available):
        # blingfire
        if blingfire:
            act_tokens = httpcache.blingfire_tokenizer(text)
            exp_tokens = [
                '"', 'We', 'saw', 'the', 'amazing', 'community', 'that', '’s', 'grown', 'up',
                'around', 'Kubernetes', ',', 'and', 'we', 'wanted', 'to', 'be', 'part', 'of',
                'that', '.', 'We', '…', '"', 'Copyright', '©', '2019', 'The', 'Linux',
                'Foundation', '®', '.', 'All', 'rights', 'reserved', '.']
            self.assertEqual(act_tokens, exp_tokens)

            act_tokens = AlchemyCacheStorage.normalize_punctuation(act_tokens, False)
            exp_tokens = [
                'We', 'saw', 'the', 'amazing', 'community', 'that', '’s', 'grown', 'up', 'around',
                'Kubernetes', 'and', 'we', 'wanted', 'to', 'be', 'part', 'of', 'that', 'We', '…',
                'Copyright', '©', '2019', 'The', 'Linux', 'Foundation', '®', 'All', 'rights',
                'reserved']
            self.assertEqual(act_tokens, exp_tokens)

    def test_compute_simhash(self):
        text = (
            "\"We saw the amazing community that’s grown up around Kubernetes, and we wanted to "
            "be part of that. We …\"\nCopyright © 2019 The Linux Foundation ®. All rights reserved."
        )

        settings = make_settings(self.region_name, use_simhash=True)
        storage = AlchemyCacheStorage(settings)

        act_value = storage.compute_simhash(text)
        exp_value = 5490512074992908592

        self.assertEqual(act_value, exp_value)

    def test_store_response_simhash(self):
        filename, url = 'test_page_1.html', 'http://www.example.com/'
        request, response = make_response_from_file(filename, url)

        settings = make_settings(self.region_name)
        settings.set('SCRACHY_USE_CONTENT_EXTRACTION', True)
        settings.set('SCRACHY_USE_SIMHASH', True)

        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request, response)

        item = storage.dump_cache()[0]

        act_value = item.response_body_text_simhash
        exp_value = 3567515302636924889
        self.assertEqual(act_value, exp_value)
        storage.close_spider(None)

        # Test there's a warning if extract content is False
        settings.set('SCRACHY_USE_CONTENT_EXTRACTION', False)
        settings.set('SCRACHY_USE_SIMHASH', True)

        storage = AlchemyCacheStorage(settings)
        with self.assertLogs('scrachy.middleware.httpcache', level='WARNING') as log_ctx:
            storage.open_spider(None)

        storage.store_response(None, request, response)

        self.assertTrue(
            "SCRACHY_USE_SIMHASH is True, but SCRACHY_USE_CONTENT_EXTRACTION is False"
            in log_ctx.output[0]
        )

        item = storage.dump_cache()[-1]

        self.assertIsNone(item.response_body_text_simhash)

    def test_store_response_content_extraction(self):
        # If store response test works then the basic content extraction
        # must be working to.
        self._test_basic_extraction()

        # Currently boilerpipe is the only other method, but I may add more.
        self._test_boilerpipe_extraction()

    def test_store_response_with_duplicates(self):
        filename1, url = 'test_page_1.html', 'http://www.example.com/'
        filename2 = 'test_page_2.html'
        request1, response1 = make_response_from_file(filename1, url)
        request2, response2 = make_response_from_file(filename2, url)

        settings = make_settings(self.region_name)

        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request1, response1)
        storage.store_response(None, request2, response2)

        items = storage.dump_cache()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].response_body_html, response1.text)
        self.assertNotEqual(items[1].response_body_html, response2.text)

        act_html = storage.reconstruct_html(items)
        self.assertEqual(act_html, response2.text)

        # Add another duplicate response. This should increase the number of
        # items in the cache, but leave the reconstructed HTML the same.
        storage.store_response(None, request2, response2)

        items = storage.dump_cache()

        act_html = storage.reconstruct_html(items)

        self.assertEqual(len(items), 3)
        self.assertEqual(act_html, response2.text)

    def test_retrieve_response_no_duplicates(self):
        filename1, url1 = 'test_page_1.html', 'http://www.example1.com/'
        filename2, url2 = 'test_page_2.html', 'http://www.example2.com/'

        # We'll store three request/responses in the cache
        request1, response1 = make_response_from_file(filename1, url1)
        request2, response2 = make_response_from_file(filename2, url2)
        request3, response3 = make_response_from_file(filename2, url2, '{param=value}')

        settings = make_settings(self.region_name)

        with tempfile.NamedTemporaryFile() as tf:
            # Add some items to the cache
            settings.set('SCRACHY_DATABASE', tf.name)
            settings.set('SCRACHY_USE_CONTENT_EXTRACTION', True)
            settings.set('SCRACHY_STORE_TEXT', True)
            settings.set('SCRACHY_USE_SIMHASH', True)

            storage = AlchemyCacheStorage(settings)
            storage.open_spider(None)
            storage.store_response(None, request1, response1)
            storage.store_response(None, request2, response2)
            storage.store_response(None, request3, response3)

            # Set the expiration to a short time period
            settings.set('HTTPCACHE_EXPIRATION_SECS', 0.1)
            storage = AlchemyCacheStorage(settings)
            storage.open_spider(None)

            # Retrieve with default settings.
            # Try to retrieve something not in the cache
            new_request, _ = make_response_from_file(filename1, 'http://acme.com')
            act_response = storage.retrieve_response(None, new_request)
            self.assertIsNone(act_response)

            # Try to retrieve something that is in the cache
            act_response1 = storage.retrieve_response(None, request1)
            act_response2 = storage.retrieve_response(None, request2)
            act_response3 = storage.retrieve_response(None, request3)

            self.assertEqual(act_response1.text, response1.text)
            self.assertEqual(act_response2.text, response2.text)
            self.assertEqual(act_response3.text, response3.text)

            settings.set('SCRACHY_RESPONSE_RETRIEVAL_METHOD', 'full')
            storage = AlchemyCacheStorage(settings)
            storage.open_spider(None)

            act_response1 = cast(CachedHtmlResponse, storage.retrieve_response(None, request1))

            self.assertIsNotNone(act_response1.scrape_timestamp)
            self.assertEqual(
                act_response1.content_extraction_method,
                storage.content_extraction_method_name
            )
            self.assertEqual(
                act_response1.content_extraction_parser,
                storage.content_extraction_parser_name
            )
            self.assertEqual(
                act_response1.simhash_hash_algorithm,
                storage.simhash_hash_algorithm_name
            )
            self.assertIsNotNone(act_response1.body_text)
            self.assertEqual(act_response1.simhash, 3567515302636924889)

            # Sleep until all items in the cache have expired.
            time.sleep(0.2)
            act_response1 = storage.retrieve_response(None, request1)
            act_response2 = storage.retrieve_response(None, request2)
            act_response3 = storage.retrieve_response(None, request3)

            self.assertIsNone(act_response1)
            self.assertIsNone(act_response2)
            self.assertIsNone(act_response3)

    def test_retrieve_response_multiple_duplicates(self):
        filename1, url = 'test_page_1.html', 'http://www.example.com/'
        filename2 = 'test_page_2.html'
        request1, response1 = make_response_from_file(filename1, url)
        request2, response2 = make_response_from_file(filename2, url)

        settings = make_settings(self.region_name)
        settings.set('SCRACHY_RESPONSE_RETRIEVAL_METHOD', 'full')

        # Store a request that has multiple duplicates.
        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request1, response1)
        storage.store_response(None, request2, response2)
        storage.store_response(None, request2, response2)

        act_response_1 = storage.retrieve_response(None, request1)
        act_response_2 = storage.retrieve_response(None, request2)

        # Since the requests all have the same url the fingerprint should be
        # the same. So, on the first insert the response will have the html
        # of response1. However, on the second insert it should be updated to
        # reflect the html of response2. If we insert response2 again it should
        # update (add an entry) the scrape_timestamp, but the html should be
        # unchanged.
        self.assertEqual(act_response_1.text, response2.text)
        self.assertEqual(act_response_2.text, response2.text)

        # Get the current time
        current_time = datetime.datetime.now(datetime.timezone.utc)

        # Now store the response again. The retrieved scrape_timestamp should
        # be after the current time.
        storage.store_response(None, request2, response2)

        act_response_2 = storage.retrieve_response(None, request2)
        act_time = act_response_2.scrape_timestamp

        # The timestamp should not be before the amount of time we slept for.
        self.assertTrue(act_time > current_time)

    # region Utility Methods
    # region Common Utilities

    # endregion Common Utilities

    # region Test Settings
    def _test_options(
            self,
            setting_name: str,
            settings: scrapy.settings.Settings,
            valid_options: Set[str]
    ):
        # Check the valid algorithms work for all features that use them.
        current_setting = settings[setting_name]
        for option in valid_options:
            settings.set(setting_name, option)

            if (('TOKENIZER' in setting_name and (option == 'blingfire' and blingfire is None))
                    or ('HASH_ALGORITHM' in setting_name
                        and (option == 'xxhash' and xxhash is None))):
                with self.assertRaises(InvalidSettingError):
                    AlchemyCacheStorage(settings)._validate_supported_options()
            else:
                try:
                    AlchemyCacheStorage(settings)._validate_supported_options()
                except InvalidSettingError:
                    self.fail("A valid option was flagged as invalid.")

        # Check that an invalid option raises an exception
        with self.assertRaises(InvalidSettingError):
            settings.set(setting_name, '<unk_option>')
            AlchemyCacheStorage(settings)._validate_supported_options()

        settings.set(setting_name, current_setting)
    # endregion Test Settings

    # region Test Content Extraction
    def _test_basic_extraction(self):
        filename, url = 'test_content_extraction.html', 'http://www.example.com/'
        request, response = make_response_from_file(filename, url)

        # Test the basic extractor
        settings = make_settings(
            self.region_name,
            use_content_extraction=True,
            store_text=True,
            content_extraction_method='basic'
        )

        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request, response)

        act_text = storage.dump_cache()[0].response_body_text
        exp_text = read_file('expected_basic.txt')

        self.assertEqual(act_text, exp_text)

        storage.clear_cache()

    def _test_boilerpipe_extraction(self):
        filename, url = 'test_content_extraction.html', 'http://www.example.com/'
        request, response = make_response_from_file(filename, url)

        # Test the default extractor
        settings = make_settings(
            self.region_name,
            use_content_extraction=True,
            store_text=True,
            content_extraction_method='boilerpipe_default'
        )

        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request, response)

        act_text = storage.dump_cache()[0].response_body_text
        exp_text = read_file('expected_boilerpipe_default.txt')

        self.assertEqual(act_text, exp_text)
        storage.clear_cache()

        settings = make_settings(
            self.region_name,
            use_content_extraction=True,
            store_text=True,
            content_extraction_method='boilerpipe_article'
        )

        storage = AlchemyCacheStorage(settings)
        storage.open_spider(None)
        storage.store_response(None, request, response)

        act_text = storage.dump_cache()[0].response_body_text
        exp_text = read_file('expected_boilerpipe_article.txt')

        self.assertEqual(act_text, exp_text)
        
    # endregion Test Content Extraction
    # endregion Utility Methods


if __name__ == '__main__':
    unittest.main()
