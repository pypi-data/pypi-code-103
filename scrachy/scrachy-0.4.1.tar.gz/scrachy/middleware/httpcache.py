##############################################################################
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

##############################################################################
#
#   In addition to the terms listed above you must also follow the terms
#   set by the 3-Clause BSD license. See the BSD_LICENSE.md file or online
#   at <https://opensource.org/licenses/BSD-3-Clause>.
#
##############################################################################

# Python Modules
import datetime
import logging
import re
import string
import urllib.parse

from typing import Optional, Any, List

# 3rd Party Modules
import bs4
import diff_match_patch
import scrapy.settings
import sqlalchemy
import sqlalchemy.orm
import w3lib.url

from scrapy.utils.python import to_bytes, to_unicode
from sqlalchemy import func

# Optional imports
from w3lib.http import headers_dict_to_raw, headers_raw_to_dict

try:
    import blingfire
except ImportError:
    blingfire = None

try:
    import boilerpy3 as bp3
except ImportError:
    bp3 = None

try:
    import html5lib
except ImportError:
    html5lib = None

try:
    import lxml
except ImportError:
    lxml = None

try:
    import simhash
except ImportError:
    simhash = None

try:
    import spookyhash
except ImportError:
    spookyhash = None

try:
    import xxhash
except ImportError:
    xxhash = None

# Project Modules
from scrachy.db.engine import session_scope
from scrachy.db.models import CacheRegion, CacheRegionSettings, CachedResponseBody, CachedRequest, \
    CachedResponseMeta, HashAlgorithm, HtmlParser, ContentExtractionMethod, Tokenizer
from scrachy.exceptions import InvalidSettingError
from scrachy.settings import get_setting, DEFAULT_SETTINGS, VALID_HASH_ALGORITHMS, VALID_DIALECTS, \
    VALID_HTML_PARSERS, VALID_CONTENT_EXTRACTION_METHODS, VALID_TOKENIZERS, \
    VALID_RESPONSE_RETRIEVAL_METHODS
from scrachy.tokenize import space_tokenizer, character_tokenizer, blingfire_tokenizer
from scrachy.utils.db import make_database_url, load_credentials
from scrachy.http import CachedHtmlResponse
from scrachy.utils.hash import request_fingerprint, make_hasher, hash_text
from scrachy.utils.numeric import slice_int, to_int64, to_uint64


log = logging.getLogger(__name__)

DOM_BLACKLIST = {'[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input'}


# region Content Extraction
def cleanup_extracted_text(content: str) -> str:
    """
    This applies a few simple rules to clean up the text extracted from an
    html document.

        1. Split on line breaks.
        2. Strip whitespace from the beginning and ending of each line.
        3. Replace all continuous sequences of whitespace characters with a
           single space.
        4. Remove any empty lines.

    :param content: The content to clean up.
    :return: The text after applying these rules.
    """
    lines = content.splitlines()
    lines = [s.strip() for s in lines]
    lines = [re.sub(r'\s+', ' ', s) for s in lines]
    lines = [s for s in lines if s]

    return '\n'.join(lines)


def basic_content_extraction(html: str, parser_name: Optional[str] = None) -> str:
    """
    Extracts the textual content from the html using a simple algorithm described
    `here <https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/>`_.
    In short it ignores blocks that are unlikely to contain meaningful content, e.g.,
    script blocks, and then strips the tags from the remaining document.

    :param html: The html content as text.
    :param parser_name: The parser to use for constructing the DOM. It can be one of the following:
           [html.parser, lxml, lxml-xml, html5lib]. By default it will use ``html.parser``, but
           lxml or html5lib are probably prefered.
    :return: Return the extracted text.
    """
    dom = bs4.BeautifulSoup(html, parser_name)

    # Remove script and style nodes from the DOM
    for node in dom(['script', 'style']):
        node.extract()

    # Find the remaining text nodes
    text_nodes = dom.find_all(text=True)

    # Only include the text from the nodes that aren't blacklisted
    valid_nodes = [t.strip() for t in text_nodes if t.parent.name not in DOM_BLACKLIST]

    # Normalize spaces
    valid_nodes = [re.sub(r'\s+', ' ', t) for t in valid_nodes]

    # Remove blank lines
    valid_nodes = [t for t in valid_nodes if t]

    return '\n'.join([t for t in valid_nodes])


# noinspection PyUnusedLocal
def boilerpipe_default_content_extraction(html: str, parser_name: Optional[str] = None) -> str:
    """
    Extract the content of the page using boilerpipe's default extractor.

    :param html: The html content (as a string)
    :param parser_name: Not used (boilerpipe uses its own parser)
    :return: The extracted content.
    """
    extractor = bp3.extractors.DefaultExtractor()
    content = extractor.get_content(html)
    return cleanup_extracted_text(content)


# noinspection PyUnusedLocal
def boilerpipe_article_content_extraction(html: str, parser_name: Optional[str] = None) -> str:
    """
    Extract the content of the page using boilerpipe's article extractor.

    :param html: The html content (as a string)
    :param parser_name: Not used (boilerpipe uses its own parser)
    :return: The extracted content.
    """
    extractor = bp3.extractors.ArticleExtractor()
    content = extractor.get_content(html)
    return cleanup_extracted_text(content)
# endregion Content Extraction


class AlchemyCacheStorage(object):
    content_extraction_switcher = {
        'basic': basic_content_extraction,
        'boilerpipe_default': boilerpipe_default_content_extraction,
        'boilerpipe_article': boilerpipe_article_content_extraction
    }
    """
    A dictionary that returns a content extraction function given its name.
    """

    tokenizer_switcher = {
        'space': space_tokenizer,
        'character': character_tokenizer,
        'blingfire': blingfire_tokenizer
    }
    """
    A dictionary that returns a tokenizing function given its name.
    """

    def __init__(self, settings: scrapy.settings.Settings):
        """
        This class implements a `scrapy cache storage backend <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#writing-your-own-storage-backend>`_
        that uses a relational database to store the cached documents. It can
        be used as a drop in replacement for Scrapy's built in storage
        backends, but it also provides additional functionality. This
        functionality uses more computational resources, especially
        when storing the responses, so if speed is the primary concern
        this backend may not appropriate.

        :param settings: The Scrapy project settings.
        """
        self._settings = settings
        self._diff_engine = diff_match_patch.diff_match_patch()
        self._diff_engine.Diff_Timeout = self.diff_timeout
        self._credentials = load_credentials(settings)
        self._region = None
        self._hash_algorithms = None
        self._html_parsers = None
        self._content_extraction_methods = None
        self._tokenizers = None
        self._is_setup = False

    # region API
    # region Properties
    # Add properties for all valid settings. At the expense of being verbose
    # this helps avoid typos and validate them (although currently there is
    # very little validation).
    @property
    def region_name(self) -> str:
        """
        Gets the region name for this cache as specified in the project
        settings. Any project using the same region name will access the same
        cached items.

        :return: The region name.
        """
        return get_setting('SCRACHY_REGION_NAME', self._settings)

    @property
    def region(self) -> CacheRegion:
        """
        The database object corresponding to the region name.

        :return: The cache region object.
        """
        return self._region

    @property
    def dialect(self) -> str:
        """
        The dialect used for connecting to the database server as specified in
        the project settings. A dialect is always required and should never be
        ``None``. For supported dialects and drivers see the
        `SQLAlchemy website <https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases>`_.

        :return: The dialect name.
        """
        return get_setting('SCRACHY_DIALECT', self._settings)

    @property
    def driver(self) -> Optional[str]:
        """
        The name of the driver to use with the database or ``None`` to use the
        default driver provided by SqlAlchemy.

        :return: The driver name.
        """
        return get_setting('SCRACHY_DRIVER', self._settings)

    @property
    def host(self) -> Optional[str]:
        """
        Returns the host name specified in the project settings. If the
        host is ``None`` in the project settings then ``localhost`` will be
        returned instead for all dialects except sqlite. Note the ``host``
        for sqlite should be ``None``, but no error will be raised if it
        is not.

        :return: The host name.
        """
        host = get_setting('SCRACHY_HOST', self._settings)

        return host if self.dialect == 'sqlite' or host is not None else 'localhost'

    @property
    def port(self) -> Optional[int]:
        """
        The port used to connect to the database as specified in the project
        settings. For sqlite this should return ``None``. ``None`` also
        represents the default port for other database dialects. An error
        is raised if the port specified in the settings can not be cast
        to an integer.

        :return: The port.
        :raises ValueError: If the port is not ``None`` and cannot be cast to
                an int.
        """
        port = get_setting('SCRACHY_PORT', self._settings)

        try:
            return port if port is None else int(port)
        except ValueError as e:
            log.error(f"If the port is set (not None) it must be an integer but got: {port}")
            raise e

    @property
    def database(self) -> Optional[str]:
        """
        The name of the database to connect to. The only time this should be
        ``None`` is when using an in memory sqlite database (which mostly
        defeats the purpose of a cache storage engine).

        :return: The name of the database.
        """
        return get_setting('SCRACHY_DATABASE', self._settings)

    @property
    def username(self) -> Optional[str]:
        """
        The user name for connecting to the database. This can be ``None``
        if the database does not require authentication.

        :return: The username.
        """
        return self._credentials.get('username')

    @property
    def password(self) -> Optional[str]:
        """
        The corresponding password for connecting to the database. This can
        be ``None`` if the database does not require authentication or uses
        another way of authenticating (e.g., a .pgpass file).

        :return: The password.
        """
        return self._credentials.get('password')

    @property
    def diff_timeout(self) -> int:
        """
        The number of seconds before the diff calculation times out. The result
        after this period should be valid, but probably not optimal.

        :return: The number of seconds.
        """
        return get_setting('SCRACHY_DIFF_TIMEOUT', self._settings)

    @property
    def fingerprint_hash_algorithm_name(self) -> str:
        """
        The name of the algorithm to use for creating the request fingerprint.
        This should chosen from one of the values in
        :const:`~scrachy.settings.VALID_HASH_ALGORITHMS`.

        :return: The name of the algorithm.
        """
        return get_setting('SCRACHY_FINGERPRINT_HASH_ALGORITHM', self._settings)

    @property
    def fingerprint_hash_algorithm(self) -> HashAlgorithm:
        """
        The database model object corresponding to the selected hash algorithm.

        :return: The object.
        """
        return self._hash_algorithms[self.fingerprint_hash_algorithm_name]

    @property
    def use_content_extraction(self) -> bool:
        """
        Whether or not the plain text content of the html is going to be
        extracted from the html.

        :return: ``True`` if the content will be extracted.
        """
        return get_setting('SCRACHY_USE_CONTENT_EXTRACTION', self._settings)

    @property
    def use_simhash(self) -> bool:
        """
        Whether or not to calculate a sim hash of the body content.

        :return: If ``True`` calculate the simhash.
        """
        return get_setting('SCRACHY_USE_SIMHASH', self._settings)

    @property
    def simhash_tokenizer_name(self) -> str:
        """
        The type of tokenizer to use for constructing shingles.
        Choose from: :const:`~scrachy.settings.VALID_TOKENIZERS`.

        :return: The name of the tokenizer.
        """
        return get_setting('SCRACHY_SIMHASH_TOKENIZER', self._settings)

    @property
    def simhash_tokenizer(self) -> Tokenizer:
        """
        The database model object corresponding to the selected tokenizer.

        :return: The object.
        """
        return self._tokenizers[self.simhash_tokenizer_name]

    @property
    def simhash_window(self) -> str:
        """
        The size of the window used to shingle the tokens.

        :return: The window size.
        """
        return get_setting('SCRACHY_SIMHASH_WINDOW', self._settings)

    @property
    def simhash_keep_punctuation(self) -> bool:
        """
        Whether or not to include punctuation when calculating the simhash.

        :return: ``True`` if punctuation should be included.
        """
        return get_setting('SCRACHY_SIMHASH_KEEP_PUNCTUATION', self._settings)

    @property
    def simhash_use_lowercase(self) -> bool:
        """
        Whether or not to lowercase the text before calculating the simhash.

        :return: ``True`` if the text should be lowercased.
        """
        return get_setting('SCRACHY_SIMHASH_USE_LOWERCASE', self._settings)

    @property
    def simhash_hash_algorithm_name(self) -> str:
        """
        The name of the algorithm to use for applying the simahash technique to
        the body text.

        :return: The name.
        """
        return get_setting('SCRACHY_SIMHASH_HASH_ALGORITHM', self._settings)

    @property
    def simhash_hash_algorithm(self) -> HashAlgorithm:
        """
        The database model object corresponding to the simhash hash algorithm
        name.

        :return: The object.
        """
        return self._hash_algorithms[self.simhash_hash_algorithm_name]

    @property
    def content_extraction_parser_name(self) -> str:
        """
        The name of the parser to use for building the DOM.

        :return: The name.
        """
        return get_setting('SCRACHY_CONTENT_EXTRACTION_PARSER', self._settings)

    @property
    def content_extraction_parser(self) -> HtmlParser:
        """
        The database model object corresponding to the HTML parser name.

        :return: The object.
        """

        return self._html_parsers[self.content_extraction_parser_name]

    @property
    def content_extraction_method_name(self) -> str:
        """
        The name of the technique used to filter out boilerplate content or
        ``None`` to use the simple default method.

        :return: The name.
        """
        return get_setting('SCRACHY_CONTENT_EXTRACTION_METHOD', self._settings)

    @property
    def content_extraction_method(self) -> ContentExtractionMethod:
        """
        The database model object corresponding to the content extraction
        method name.

        :return: The object.
        """
        return self._content_extraction_methods[self.content_extraction_method_name]

    @property
    def store_text(self) -> bool:
        """
        Whether or not to store the extracted text and processed by the
        boilerplate removal process in the cache.

        :return: ``True`` if the content should be stored.
        """
        return get_setting('SCRACHY_STORE_TEXT', self._settings)

    @property
    def response_retrieval_method(self) -> str:
        """
        The name of the response retrieval method.

        This determines how much information to retrieve in the response.

        minimal
            This returns the minimal amount of information and should be the
            fastest because it does not require any joins. However, it will
            return null values for the response status and headers. Use this
            method of you don't need these or the more detailed information.
        standard
            This returns the standard information an :class:`scrapy.http.HtmlResponse`
            does.
        full
            This returns a :class:`scrachy.http.CachedResponse`, which contains
            all the information available for an item in the cache.

        :return: The the type of response to retrieve.
        """
        return get_setting('SCRACHY_RESPONSE_RETRIEVAL_METHOD', self._settings)

    @property
    def expiration_secs(self) -> int:
        """
        The value of the scrapy HTTPCACHE_EXPIRATION_SECS setting.

        :return: The number of seconds before the cached item becomes stale.
                 Stale items will be redownloaded and processed through the
                 normal pipeline regardless if they are in the cache or not.
        """
        return get_setting('HTTPCACHE_EXPIRATION_SECS', self._settings, 0)

    # endregion Properties

    # region Scrapy API
    # noinspection PyUnusedLocal
    def open_spider(self, spider: scrapy.spiders.Spider):
        """
        Connect to the database, validate the settings and set up the database
        tables if necessary.

        :param spider: The Scrapy spider.
        """
        if self.region_name is None:
            self._settings.set('SCRACHY_REGION_NAME', spider.name)

        self._load_options()

        self.validate_and_assign_settings()

    # noinspection PyUnusedLocal
    def close_spider(self, spider: scrapy.spiders.Spider):
        """
        Do nothing.

        :param spider: The Scrapy spider
        """
        pass

    def retrieve_response(
            self,
            spider: scrapy.spiders.Spider,
            request: scrapy.http.Request
    ) -> Optional[CachedHtmlResponse]:
        """
        Retrieves an item from the cache if it exists, otherwise this returns
        ``None`` to signal downstream processes to continue retrieving the
        page normally. Depending on the value of the
        ``SCRACHY_RESPONSE_RETRIEVAL_METHOD`` setting more or less information
        may be returned in the response.

        :param spider: The Scrapy Spider requesting the data.
        :param request: The request describing what information to retrieve.
        :return: If the page is in the cache then this will return a
                 :class:`~scrachy.http.CachedHtmlResponse`, otherwise it will
                 return ``None``.
        """
        cached_pages = self._read_data(spider, request)

        # We didn't find anything (or the cache is expired)
        if not cached_pages:
            return None

        # Reconstruct the html by piecing together the base document and
        # subsequent patches if necessary.
        body = self.reconstruct_html(cached_pages)

        # Create a new Response from the cached items.
        if self.response_retrieval_method == 'minimal':
            # Return only the minimal amount of information.
            # If you don't need the other information this will be the fastest
            # method because it does not require any joins.
            kwargs = {
                'request': request,
                'url': request.url,
                'headers': None,
                'status': None,
                'body': body
            }
        elif self.response_retrieval_method == 'standard':
            # This will basically return the same content as Scrapy's
            # downloader or storage engines will.

            # Finds the last page whose status or headers are not None.
            most_recent_page = self._get_most_recent_page(cached_pages)

            kwargs = {
                'request': request,
                'url': request.url,
                'headers': headers_raw_to_dict(to_bytes(most_recent_page.response_headers)),
                'status': most_recent_page.response_status,
                'body': body
            }
        else:
            # This will return (almost) all the data Scrachy has about this
            # cached item.
            scrape_timestamp = cached_pages[-1].scrape_timestamp
            most_recent_page = self._get_most_recent_page(cached_pages)

            kwargs = {
                'scrape_timestamp': scrape_timestamp,
                'content_extraction_method': most_recent_page.content_extraction_method,
                'content_extraction_parser': most_recent_page.content_extraction_parser,
                'simhash_hash_algorithm': most_recent_page.simhash_hash_algorithm,
                'html_number_of_bytes': most_recent_page.response_body_html_number_of_bytes,
                'text_number_of_bytes': most_recent_page.response_body_text_number_of_bytes,
                'body_text': most_recent_page.response_body_text,
                'simhash_value': to_uint64(most_recent_page.response_body_text_simhash),
                'request': request,
                'url': request.url,
                'headers': headers_raw_to_dict(to_bytes(most_recent_page.response_headers)),
                'status': most_recent_page.response_status,
                'body': body
            }

        return self._make_response(**kwargs)

    # noinspection PyUnusedLocal
    def store_response(
            self,
            spider: scrapy.spiders.Spider,
            request: scrapy.http.Request,
            response: scrapy.http.Response
    ):
        """
        Stores the response in the cache.

        :param spider: The Scrapy Spider issuing the request.
        :param request: The request describing what data is desired.
        :param response: The response to be stored in the cache as created by
               Scrapy's standard downloading process.
        """
        fingerprint = request_fingerprint(
            request,
            make_hasher[self.fingerprint_hash_algorithm_name]()
        )

        # First find out if there are any items in the cache with the same
        # request fingerprint.
        with session_scope() as session:
            cached_pages = self._find_cached_pages(session, fingerprint)
            self._insert_into_cache(session, fingerprint, request, response, cached_pages)
    # endregion Scrapy API

    # region Extended API
    # region Class Methods

    @classmethod
    def extract_text(cls, html: str, method: str, parser: str) -> str:
        """
        Extract the textual content from an html document using the specified
        extraction method and DOM parsing method.

        :param html: The html to extract the text from.
        :param method: The extraction method. This should be one of the choices
               from :data:`~scrachy.settings.VALID_CONTENT_EXTRACTION_METHODS`.

               basic
                 This uses a very simple method that extracts the content
                 from all text nodes, but excludes some regions that are
                 unlikely to have useful information like ``script`` and
                 ``style`` tags.
               boilerpipe_default
                 This first tries to find the main content area using a set
                 of heuristics and then extract the text from this region.
                 See the `boilerpipe <https://code.google.com/archive/p/boilerpipe/>`_
                 website and the `python port <https://github.com/jmriebold/BoilerPy3>`_
                 used here for more information.
               boilerpipe_article
                 This also uses boilerpipe to find and extract the main content
                 of the page, but uses heuristics tailored to news articles.

        :param parser: The DOM parser to use. This should be one of the choices
               from :const:`~scrachy.settings.VALID_HTML_PARSERS`.
        :return: The extracted text.
        """
        return cls.content_extraction_switcher[method](html, parser)

    @classmethod
    def normalize_punctuation(cls, tokens: List[str], keep_punctuation: bool) -> List[str]:
        """
        Strip the tokens of punctuation if ``keep_punctuation`` is ``False``.
        Otherwise this returns the ``tokens`` as is.

        :param tokens: The tokens to normalize (strip punctuation of).
        :param keep_punctuation: If ``True`` the tokens will be returned as is.
        :return: The normalized tokens.
        """
        if keep_punctuation:
            return tokens

        result = [t.translate(str.maketrans('', '', string.punctuation)) for t in tokens]

        # Remove tokens that are now empty
        return [t for t in result if t]
    # endregion Class Methods

    def validate_and_assign_settings(self):
        """
        This makes sure that any setting starting with the prefix ``SCRACHY``
        is known to the storage backend.

        It performs some minor validation like checking to make sure the
        port is an integer and a host name is specified unless the dialect is
        sqlite. It is still primarily up to the user to ensure the database
        connection properties are valid for the type of database being used.

        :raises InvalidSettingError: If there are:

                * unknown scrachy settings.
                * invalid database settings.
                * an option to a setting that is not valid.
                * the hash algorithm specified in the project settings used to
                  create the request fingerprint is different than the one
                  already used for this cache region.
        """

        self._validate_unknown_settings()
        self._validate_supported_options()
        self._validate_database_parameters()
        self._validate_and_assign_region()
        self._validate_fingerprint()

    def reconstruct_html(self, pages: List[CachedResponseBody]) -> Optional[str]:
        """
        Reconstruct the html from a list of cached items from the same region and
        request_fingerprint. The ``pages`` must be sorted in ascending
        timestamp order (earliest date first).

        :param pages: The cached pages.
        :return: The reconstructed html for the most recent scrape or ``None``
                 if there was nothing in the cache already.
        """
        # If the page list is empty return None
        if not pages:
            return None

        # If there is only one page, the content must be the full html
        if len(pages) == 1:
            return pages[0].response_body_html

        # Otherwise we need to reconstruct the most recent scrape from the sequence
        # of patches.
        diff_engine = self._diff_engine
        base_html = pages[0].response_body_html

        # Note patch_fromText returns a list so the following will be a list
        # of lists.
        patches = [diff_engine.patch_fromText(p.response_body_html) for p in pages[1:]]

        # Flatten the list of patches
        patches = [p for patch_list in patches for p in patch_list]

        # Return the resulting text
        return diff_engine.patch_apply(patches, base_html)[0]

    def compute_simhash(self, txt: str) -> Optional[int]:
        """
        Compute the simhash from the given text. If ``SCRACHY_USE_SIMHASH`` is
        ``False`` or the ``simhash-py`` package is not installed then ``None``
        will be returned.

        If the hash algorithm selected for computing the simhash returns
        digests that are greater than 64 bits, only the first 64 bits are
        used.

        :param txt: The text to compute.
        :return: The simhash as a 64 bit integer.
        """
        if not self.use_simhash:
            return None

        if simhash is None:
            log.warning(f"simhash-py is not installed so the simhash will not be calculated")
            return None

        tokens = self.tokenizer_switcher[self.simhash_tokenizer_name](txt)
        tokens = self.normalize_punctuation(tokens, self.simhash_keep_punctuation)
        tokens = [t.lower() for t in tokens] if self.simhash_use_lowercase else tokens
        shingles = [str(s) for s in simhash.shingle(tokens, self.simhash_window)]

        try:
            hashes = [
                slice_int(hash_text(s, make_hasher[self.simhash_hash_algorithm_name]()), 64)
                for s in shingles
            ]
        except ValueError:
            raise ValueError("The hash algorithm for simhash must be at least 64 bits.")

        return to_int64(simhash.compute(hashes))

    @classmethod
    def clear_cache(cls):
        with session_scope() as session:
            session.query(CachedResponseBody).delete()
            session.query(CachedRequest).delete()
            session.query(CachedResponseMeta).delete()

    @classmethod
    def dump_cache(cls) -> list:
        """
        Dump the contents of the cache. This is not recommended except for
        debugging.

        :return: A list of SQLAlchemy result objects that contains all
                 the items in the cache.
        """
        with session_scope() as session:
            fingerprint_hash = sqlalchemy.orm.aliased(HashAlgorithm)
            simhash_hash = sqlalchemy.orm.aliased(HashAlgorithm)

            # noinspection PyUnresolvedReferences
            items = session.query(
                CacheRegion.name.label('region_name'),
                CachedResponseBody.request_fingerprint,
                CachedResponseBody.scrape_timestamp,
                CachedRequest.url.label('request_url'),
                CachedRequest.netloc.label('request_netloc'),
                CachedRequest.method.label('request_method'),
                CachedRequest.body.label('request_body'),
                CachedResponseMeta.response_status,
                CachedResponseMeta.response_headers,
                fingerprint_hash.name.label('fingerprint_hash_algorithm'),
                ContentExtractionMethod.name.label('content_extraction_method'),
                HtmlParser.name.label('content_extraction_parser'),
                simhash_hash.name.label('simhash_hash_algorithm'),
                CachedResponseMeta.response_body_html_number_of_bytes,
                CachedResponseMeta.response_body_text_number_of_bytes,
                CachedResponseMeta.response_body_text,
                CachedResponseBody.response_body_html,
                CachedResponseMeta.response_body_text_simhash
            ).select_from(
                CachedResponseBody
            ).outerjoin(
                CacheRegion,
                CacheRegion.id == CachedResponseBody.region_id,
            ).outerjoin(
                CacheRegionSettings,
                CacheRegionSettings.region_id == CachedResponseBody.region_id
            ).outerjoin(
                CachedRequest,
                sqlalchemy.and_(
                    CachedRequest.region_id == CachedResponseBody.region_id,
                    CachedRequest.scrape_timestamp == CachedResponseBody.scrape_timestamp,
                    CachedRequest.fingerprint == CachedResponseBody.request_fingerprint
                )
            ).outerjoin(
                CachedResponseMeta,
                sqlalchemy.and_(
                    CachedResponseMeta.region_id == CachedResponseBody.region_id,
                    CachedResponseMeta.scrape_timestamp == CachedResponseBody.scrape_timestamp,
                    CachedResponseMeta.request_fingerprint == CachedResponseBody.request_fingerprint
                )
            ).outerjoin(
                ContentExtractionMethod,
                ContentExtractionMethod.id == CachedResponseMeta.content_extraction_method_id
            ).outerjoin(
                HtmlParser,
                HtmlParser.id == CachedResponseMeta.content_extraction_parser_id
            ).outerjoin(
                fingerprint_hash,
                fingerprint_hash.id == CacheRegionSettings.fingerprint_hash_algorithm_id
            ).outerjoin(
                simhash_hash,
                simhash_hash.id == CachedResponseMeta.simhash_hash_algorithm_id
            ).order_by(
                CachedResponseBody.scrape_timestamp
            ).all()
            session.expunge_all()

            return items
    # endregion Extended API
    # endregion API

    # region Utility Methods
    # region Validation
    def _validate_unknown_settings(self):
        """
        Check that there aren't any unknown scrachy settings (e.g., typos).

        :raises InvalidSettingError:
        """
        for key, value in self._settings.items():
            if key.startswith('SCRACHY') and key not in DEFAULT_SETTINGS.keys():
                raise InvalidSettingError(f"Unknown scrachy setting: {key}")

    def _validate_supported_options(self):
        """
        Make sure the parameters for settings that take one are valid.

        :raises InvalidSettingError:
        """
        # Make sure the diff timeout is valid
        if self.diff_timeout < 0:
            log.warning(
                f"The diff timeout is less than 0 (={self.diff_timeout}). "
                f"Setting it to 0 (infinity)."
            )
            self._settings['SCRACHY_DIFF_TIMEOUT'] = 0

        # Check to make sure the hash algorithms are known and available
        self._validate_hash_algorithm(self.fingerprint_hash_algorithm_name)
        self._validate_hash_algorithm(self.simhash_hash_algorithm_name)

        # Log a warning, but don't raise and exception in case the user wants to use
        # one of the dialects maintained externally from SqlAlchemy.
        if self.dialect not in VALID_DIALECTS:
            log.warning(
                f"Unsupported database dialect '{self.dialect}'. "
                f"The officially supported dialects are: {VALID_DIALECTS}"
            )

        valid_parsers = self._html_parsers or VALID_HTML_PARSERS
        if self.content_extraction_parser_name not in valid_parsers:
            raise InvalidSettingError(
                f"Unknown html parser '{self.content_extraction_parser_name}' "
                f"The supported options are: {valid_parsers}"
            )

        if 'lxml' in self.content_extraction_parser_name and lxml is None:
            raise InvalidSettingError("You must install lxml before using it.")

        if self.content_extraction_parser_name == 'html5lib' and html5lib is None:
            raise InvalidSettingError("You must install html5lib before using it.")

        valid_methods = self._content_extraction_methods or VALID_CONTENT_EXTRACTION_METHODS
        if self.content_extraction_method_name not in valid_methods:
            raise InvalidSettingError(
                f"Unknown content extraction method '{self.content_extraction_method_name}': "
                f"The supported options are: {valid_methods}"
            )

        valid_tokenizers = self._tokenizers or VALID_TOKENIZERS
        if self.simhash_tokenizer_name not in valid_tokenizers:
            raise InvalidSettingError(
                f"Unknown simhash tokenizer '{self.simhash_tokenizer_name}'. "
                f"The supported option are: {valid_tokenizers}"
            )

        if self.simhash_tokenizer_name == 'blingfire' and blingfire is None:
            raise InvalidSettingError("You must install BlingFire before using it.")

        valid_response_methods = VALID_RESPONSE_RETRIEVAL_METHODS
        if self.response_retrieval_method not in valid_response_methods:
            raise InvalidSettingError(
                f"Unknown response retrieval method '{self.response_retrieval_method}'. "
                f"The supported option are: {valid_response_methods}"
            )

        if self.use_simhash and not self.use_content_extraction:
            log.warning(
                "SCRACHY_USE_SIMHASH is True, but SCRACHY_USE_CONTENT_EXTRACTION is False. "
                "Computing the simhash is dependent on extracting the content of the page. "
                "No simhash will be computed or stored in the database."
            )

        if self.store_text and not self.use_content_extraction:
            log.warning(
                "SCRACHY_STORE_TEXT is True, but SCRACHY_USE_CONTENT_EXTRACTION is False. "
                "Storing the extracted content text is dependent on using content extraction. "
                "No content text will be stored in the cache."
            )

    def _validate_hash_algorithm(self, hash_name: str):
        # The hash algorithms are only populated once the spider is opened.
        # If you want to call this before opening the spider, fall back
        # to the algorithms declared in the code. However, these might not
        # match what's in the database so, prefer to use the database items.
        valid_algorithms = self._hash_algorithms or VALID_HASH_ALGORITHMS
        if hash_name not in valid_algorithms:
            raise InvalidSettingError(
                f"The hash algorithm is unsupported: {hash_name}. "
                f"The supported option are: {valid_algorithms}"
            )

        if hash_name.startswith('spooky') and spookyhash is None:
            raise InvalidSettingError(
                f"You are trying to use spookyhash, but it is not available. "
                f"Please install it first."
            )

        if hash_name.startswith('xxhash') and xxhash is None:
            raise InvalidSettingError(
                f"You are trying to use xxhash, but it is not available. "
                f"Please install it first."
            )

    def _validate_database_parameters(self):
        """
        Check to make sure the database parameters are valid.

        :raises InvalidSettingError:
        """

        if self.port and not isinstance(self.port, int):
            raise InvalidSettingError(
                f"If the port is specified it must be an integer, but was: {self.port}"
            )

        if self.dialect != 'sqlite' and self.database is None:
            raise InvalidSettingError(
                "You must specify a database name for dialects except sqlite."
            )

        if self.dialect == 'sqlite' and self.driver == 'pysqlcipher':
            raise InvalidSettingError("The pysqlcipher driver is not supported.")

    def _validate_and_assign_region(self):
        with session_scope() as session:
            # Check if there is already a region with the given name
            cache_region = session.query(CacheRegion).filter_by(name=self.region_name).one_or_none()

            if not cache_region:
                max_region_id = session.query(func.max(CacheRegion.id)).scalar()
                region_id = max_region_id + 1 if max_region_id else 1
                cache_region = CacheRegion(name=self.region_name, id=region_id)
                session.add(cache_region)

                # Insert the object into the database
                session.commit()

                # Without this call the expunge won't work properly and the
                # newly created region will be seen as unassociated.
                session.refresh(cache_region)

            session.expunge_all()

        self._region = cache_region

    def _validate_fingerprint(self):
        """
        Get the current settings from the database and check they are compatible
        with the project settings. Depending on the incompatible settings handler
        this may update the project settings.

        :raises InvalidSettingError: If the request_fingerprint hashing algorithm
                is different between the database and the project settings. It
                will also raise an exception if any of the other settings are
                different and the handler is set to ``raise``.
        """
        with session_scope() as session:
            # noinspection PyUnresolvedReferences
            cache_settings = session.query(
                CacheRegionSettings
            ).filter(
                CacheRegionSettings.region == self.region
            ).one_or_none()

            # If there aren't any settings for this region then we will set
            # them and return.
            if not cache_settings:
                cache_settings = CacheRegionSettings(
                    region=self.region,
                    fingerprint_hash_algorithm=self.fingerprint_hash_algorithm
                )
                session.add(cache_settings)
                return

            if cache_settings.fingerprint_hash_algorithm.name != self.fingerprint_hash_algorithm_name:
                cache_algorithm = cache_settings.fingerprint_hash_algorithm.name
                project_algorithm = self.fingerprint_hash_algorithm.name

                raise InvalidSettingError(
                    f"The cached fingerprint hash algorithm is different from the project "
                    f"settings: {cache_algorithm} != {project_algorithm}"
                )

    def _validate_cache_setting(
            self,
            setting_name: str,
            cache_value: Any,
            project_value: Any,
            handler: str
    ):
        if cache_value == project_value:
            # There's nothing to do
            return

        msg = (
            f"The cache setting value ({cache_value}) and project value ({project_value}) "
            f"do not match for {setting_name}."
        )
        log.warning(msg)

        if handler == 'raise':
            raise InvalidSettingError(msg)

        if handler == 'use_database':
            self._settings.set(setting_name, cache_value)

        # Otherwise use the project value (which is already set).
    # endregion Validation

    # region Manage Database
    def _make_engine(self) -> sqlalchemy.engine.Engine:
        database_url = make_database_url(self._settings)

        return sqlalchemy.create_engine(database_url)

    def _load_options(self):
        with session_scope() as session:
            hash_algorithms = session.query(HashAlgorithm).all()
            html_parsers = session.query(HtmlParser).all()
            content_extaction_methods = session.query(ContentExtractionMethod).all()
            tokenizers = session.query(Tokenizer).all()

            self._hash_algorithms = {a.name: a for a in hash_algorithms}
            self._html_parsers = {p.name: p for p in html_parsers}
            self._content_extraction_methods = {m.name: m for m in content_extaction_methods}
            self._tokenizers = {t.name: t for t in tokenizers}

            session.expunge_all()
    # endregion Manage Database

    # region Store Response Utilities
    def _insert_into_cache(
            self,
            session: sqlalchemy.orm.session.Session,
            fingerprint: bytes,
            request: scrapy.http.Request,
            response: scrapy.http.Response,
            cached_pages: List[CachedResponseBody]
    ):
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        cached_html = self.reconstruct_html(cached_pages)
        has_changed = cached_html != response.text

        self._insert_response_body(
            session,
            response,
            self._diff_engine,
            self.region,
            timestamp,
            fingerprint,
            cached_html,
            has_changed
        )

        # Only insert the other items if the cached html is different from the
        # response html
        if has_changed:
            self._insert_request(session, request, timestamp, fingerprint)
            self._insert_meta(session, response, timestamp, fingerprint)

    @classmethod
    def _insert_response_body(
            cls,
            session: sqlalchemy.orm.session.Session,
            response: scrapy.http.Response,
            diff_engine: diff_match_patch,
            region: CacheRegion,
            scrape_timestamp: datetime.datetime,
            fingerprint: bytes,
            cached_html: Optional[str],
            has_changed: bool
    ):
        cached_response_body = CachedResponseBody(
            region=region,
            scrape_timestamp=scrape_timestamp,
            request_fingerprint=fingerprint
        )

        if cached_html is None:
            # If the cached html is None, then the page does not exist in the
            # database. So, use the full text.
            cached_response_body.response_body_html = response.text
        elif has_changed:
            # If the current response html is different than the cached version
            # create a patch and store it in the database. Otherwise don't
            # store anything in the html column.
            patch = diff_engine.patch_make(cached_html, response.text)
            cached_response_body.response_body_html = diff_engine.patch_toText(patch)

        session.add(cached_response_body)

    def _insert_request(
            self,
            session: sqlalchemy.orm.session.Session,
            request: scrapy.http.Request,
            scrape_timestamp: datetime.datetime,
            fingerprint: bytes
    ):
        cached_request = CachedRequest(
            region=self.region,
            scrape_timestamp=scrape_timestamp,
            fingerprint=fingerprint,
            url=w3lib.url.canonicalize_url(request.url),
            netloc=urllib.parse.urlparse(request.url).netloc,
            body=request.body,
        )
        cached_request.method = request.method

        session.add(cached_request)

    def _insert_meta(
            self,
            session: sqlalchemy.orm.session.Session,
            response: scrapy.http.Response,
            scrape_timestamp: datetime.datetime,
            fingerprint: bytes
    ):
        # Make the medatadata item

        # Extracting the text is optional
        if self.use_content_extraction:
            response_body_text = self.extract_text(
                response.text,
                self.content_extraction_method_name,
                self.content_extraction_parser_name
            )

            text_number_of_bytes = len(response_body_text)

            # Simhash is contingent on extracting the text.
            simhash_value = self.compute_simhash(response_body_text)

        else:
            response_body_text = None
            text_number_of_bytes = None
            simhash_value = None

        cached_metadata = CachedResponseMeta(
            region=self.region,
            scrape_timestamp=scrape_timestamp,
            request_fingerprint=fingerprint,
            response_status=response.status,
            response_headers=to_unicode(headers_dict_to_raw(response.headers)),
            content_extraction_method=self.content_extraction_method,
            content_extraction_parser=self.content_extraction_parser,
            response_body_html_number_of_bytes=len(to_bytes(response.text)),
            response_body_text_number_of_bytes=text_number_of_bytes,
            simhash_hash_algorithm=self.simhash_hash_algorithm,
            response_body_text_simhash=simhash_value
        )

        # Storing the text is also optional
        if self.store_text:
            cached_metadata.response_body_text = response_body_text

        session.add(cached_metadata)
    # endregion Store Response Utilities

    # region Retrieve Response Utilities
    # noinspection PyUnusedLocal
    def _read_data(
            self,
            spider: scrapy.spiders.Spider,
            request: scrapy.http.Request
    ) -> Optional[List[CachedResponseBody]]:
        fingerprint = request_fingerprint(
            request,
            make_hasher[self.fingerprint_hash_algorithm_name]()
        )
        scrape_timestamp = self._find_scrape_timestamp(fingerprint)

        # A missing timestamp indicates the data is not in the cache.
        if not scrape_timestamp:
            return None

        now = datetime.datetime.now(datetime.timezone.utc)
        time_diff = (now - scrape_timestamp).total_seconds()

        # If the item isn't found in the cache or it's been too long since
        # we've scraped the page, then don't use the cached item.
        if 0 < self.expiration_secs < time_diff:
            return None

        with session_scope() as session:
            cached_pages = self._find_cached_pages(session, fingerprint)
            session.expunge_all()
            return cached_pages

    def _find_scrape_timestamp(self, fingerprint: bytes) -> datetime.datetime:
        with session_scope() as session:
            timestamp = session.query(
                CachedResponseBody.scrape_timestamp
            ).filter_by(
                region=self.region,
                request_fingerprint=fingerprint
            ).order_by(
                CachedResponseBody.scrape_timestamp.desc()
            ).first()

            return timestamp[0] if timestamp else None
    # endregion Retrieve Response Utilities

    # region Common Utilities
    def _get_hasher(self, name: str, default: str):
        hasher = self._settings.get(f'SCRACHY_{name}_HASH_ALGORITHM', default)

        if 'xxhash' in hasher and xxhash is None:
            log.warning(
                f"xxhash is unavailable. Please run `pip install xxhash` to use it. "
                f"Using {default} instead."
            )
            hasher = default

        return hasher

    def _find_cached_pages(
            self,
            session: sqlalchemy.orm.session.Session,
            fingerprint: bytes
    ) -> List[CachedResponseBody]:
        if self.response_retrieval_method == 'minimal':
            return self._find_minimal_pages(session, fingerprint)

        if self.response_retrieval_method == 'standard':
            return self._find_standard_pages(session, fingerprint)

        if self.response_retrieval_method == 'full':
            return self._find_full_pages(session, fingerprint)

        raise InvalidSettingError(f"Unknown retrieval method: {self.response_retrieval_method}")

    def _find_minimal_pages(
            self,
            session: sqlalchemy.orm.session.Session,
            fingerprint: bytes
    ) -> List[CachedResponseBody]:
        return session.query(
            CachedResponseBody.response_body_html,
        ).select_from(
            CachedResponseBody
        ).filter(
            CachedResponseBody.region == self.region,
            CachedResponseBody.request_fingerprint == fingerprint,
        ).order_by(
            CachedResponseBody.scrape_timestamp
        ).all()

    def _find_standard_pages(
            self,
            session: sqlalchemy.orm.session.Session,
            fingerprint: bytes
    ) -> List[CachedResponseBody]:
        return session.query(
            CachedResponseBody.response_body_html,
            CachedResponseMeta.response_status,
            CachedResponseMeta.response_headers
        ).select_from(
            CachedResponseBody
        ).join(
            CachedResponseMeta,
            sqlalchemy.and_(
                CachedResponseMeta.region_id == CachedResponseBody.region_id,
                CachedResponseMeta.request_fingerprint == CachedResponseBody.request_fingerprint,
                CachedResponseBody.scrape_timestamp == CachedResponseMeta.scrape_timestamp
            )
        ).filter(
            CachedResponseBody.region == self.region,
            CachedResponseBody.request_fingerprint == fingerprint,
            CachedResponseMeta.request_fingerprint is not None
        ).order_by(
            CachedResponseBody.scrape_timestamp
        ).all()

    def _find_full_pages(
            self,
            session: sqlalchemy.orm.session.Session,
            fingerprint: bytes
    ) -> List[CachedResponseBody]:
        pages = session.query(
            CachedResponseBody.scrape_timestamp,
            CachedResponseBody.response_body_html,
            CachedResponseMeta.response_status,
            CachedResponseMeta.response_headers,
            ContentExtractionMethod.name.label('content_extraction_method'),
            HtmlParser.name.label('content_extraction_parser'),
            CachedResponseMeta.response_body_text,
            CachedResponseMeta.response_body_html_number_of_bytes,
            CachedResponseMeta.response_body_text_number_of_bytes,
            HashAlgorithm.name.label('simhash_hash_algorithm'),
            CachedResponseMeta.response_body_text_simhash
        ).select_from(
            CachedResponseBody
        ).outerjoin(
            CachedResponseMeta,
            sqlalchemy.and_(
                CachedResponseMeta.region_id == CachedResponseBody.region_id,
                CachedResponseMeta.request_fingerprint == CachedResponseBody.request_fingerprint,
                CachedResponseMeta.scrape_timestamp == CachedResponseBody.scrape_timestamp
            )
        ).outerjoin(
            ContentExtractionMethod,
            ContentExtractionMethod.id == CachedResponseMeta.content_extraction_method_id
        ).outerjoin(
            HtmlParser,
            HtmlParser.id == CachedResponseMeta.content_extraction_parser_id
        ).outerjoin(
            HashAlgorithm,
            HashAlgorithm.id == CachedResponseMeta.simhash_hash_algorithm_id
        ).filter(
            CachedResponseBody.region == self.region,
            CachedResponseBody.request_fingerprint == fingerprint,
        ).order_by(
            CachedResponseBody.scrape_timestamp
        ).all()

        return pages

    @classmethod
    def _get_most_recent_page(
            cls,
            cached_pages: List
    ):
        for i in range(len(cached_pages) - 1, -1, -1):
            page = cached_pages[i]
            if page.response_status or page.response_headers:
                return page

        raise ValueError("There appears to be no valid page in the cache.")

    def _make_response(self, **kwargs):
        try:
            # First try to use the encoding from the cached information
            response = CachedHtmlResponse(**kwargs)
        except TypeError:
            # If that fails, use the default encoding
            encoding = get_setting('SCRACHY_DEFAULT_ENCODING', self._settings)
            response = CachedHtmlResponse(encoding=encoding, **kwargs)

            log.debug(
                f"Unable to find an appropriate encoding for the page. "
                f"Using '{encoding}' instead."
            )

        return response
    # endregion Common Utilities
    # endregion Utility Methods
