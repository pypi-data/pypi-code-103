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
import logging
import re

# 3rd Party Modules
from typing import Optional

from scrapy.exceptions import IgnoreRequest
import scrapy.settings

# Project Modules
from scrachy.db.engine import session_scope
from scrachy.db.models import CachedResponseBody, CacheRegion
from scrachy.settings import get_setting
from scrachy.utils.hash import request_fingerprint, make_hasher


log = logging.getLogger(__name__)


class IgnoreCachedResponse(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings: scrapy.settings.Settings):
        """
        Sometimes you scrape the same domains multiple times looking for
        new content. However, when crawling them you might encounter pages that
        you have already scraped. If your extraction rules have not changed
        since the last crawl it may not be worth reprocessing those pages.

        This middleware will look to see if the current request is already in
        the cache and is not stale (i.e., is not older than the value of
        ``HTTPCACHE_EXPIRATION_SECS``). If these conditions are true, this
        middleware will ignore those requests.

        There are several options to disable skipping individual pages.

        * You can specify a set of patterns to match against the
          request url. Any pattern that matches a part of the url will be
          processed (not ignored) regardless of whether it is in the cache or
          not. For example, this might be useful after changing parsing rules
          for a page or pages. These are specified using the
          ``SCRACHY_SKIP_EXCLUDE_URL_PATTERNS`` setting, which takes a list of
          strings which can be compiled to regular expressions.
        * You can set the a new request meta key, ``dont_ignore`` to ``True``.
        * Any page that is already excluded from caching via the ``dont_cache``
          request meta key will never be skipped.

        :param settings: The project settings.
        """
        self._region_name = get_setting('SCRACHY_REGION_NAME', settings)
        self._fingerprint_hasher = get_setting('SCRACHY_FINGERPRINT_HASH_ALGORITHM', settings)
        self._exclude_patterns = get_setting('SCRACHY_IGNORE_EXCLUDE_URL_PATTERNS', settings)
        self._exclude_patterns = [re.compile(p) for p in self._exclude_patterns]
        self._expiration_secs = get_setting('HTTPCACHE_EXPIRATION_SECS', settings)

    # noinspection PyUnusedLocal
    def process_request(self, request: scrapy.http.Request, spider: scrapy.spiders.Spider):
        """

        :param request: The Scrapy request.
        :param spider: The Scrapy Spider issuing the request.

        :raises IgnoreRequest: If the item is already cached and it has not
                been flagged to process normally.
        """
        # If dont_cache or dont_skip is set then don't skip the item.
        if request.meta.get('dont_cache') or request.meta.get('dont_ignore'):
            return

        url = request.url

        # Otherwise check to see if the request is already in the cache and
        # skip further processing if it is.
        fingerprint = request_fingerprint(request, make_hasher[self._fingerprint_hasher]())
        timestamp = self._get_timestamp(fingerprint)
        is_cached = timestamp is not None

        # If the item is not in the cache, then don't ignore it
        if not is_cached:
            return

        now = datetime.datetime.now()

        # Make the datetime timezone aware (and use the same timezone that was
        # stored in the database).
        now = now.replace(tzinfo=timestamp.tzinfo)

        is_expired = 0 < self._expiration_secs < (now - timestamp).total_seconds()

        # If the item in the cache is expired, don't ignore it.
        if is_expired:
            return

        # If the url is in the exclusion list then never skip request even if
        # it is already in the cache.
        for pattern in self._exclude_patterns:
            if pattern.search(url):
                return

        # Otherwise ignore the cached request
        raise IgnoreRequest()

    def _get_timestamp(self, fingerprint: bytes) -> Optional[datetime.datetime]:
        with session_scope() as session:
            item = session.query(
                CachedResponseBody.scrape_timestamp
            ).select_from(
                CachedResponseBody
            ).join(
                CacheRegion,
                CacheRegion.id == CachedResponseBody.region_id
            ).filter(
                CacheRegion.name == self._region_name,
                CachedResponseBody.request_fingerprint == fingerprint
            ).first()

            return None if item is None else item[0]
