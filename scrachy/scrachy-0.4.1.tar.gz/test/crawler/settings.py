#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software = you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation either version 3 of the License or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not see <https =//www.gnu.org/licenses/>.

# Python Modules
import os
import tempfile

# 3rd Party Modules

# Project Modules

# Scrachy Settings
# General Settings
SCRACHY_REGION_NAME = 'books'
SCRACHY_DIFF_TIMEOUT = 1.0
# I suggest using xxhash128 or spooky128, but they require additional installation.
SCRACHY_FINGERPRINT_HASH_ALGORITHM = 'sha1'

# Database Settings
SCRACHY_DIALECT = 'sqlite'
SCRACHY_DRIVER = None
SCRACHY_HOST = None
SCRACHY_PORT = None
SCRACHY_DATABASE = os.path.join(tempfile.gettempdir(), 'scrachy-books-cache.db')
SCRACHY_SCHEMA = None
SCRACHY_CREDENTIALS_FILE = None

# Content Extraction Settings
SCRACHY_USE_CONTENT_EXTRACTION = True
SCRACHY_STORE_TEXT = False
# I suggest using lxml or html5lib, but they require additional installation.
SCRACHY_CONTENT_EXTRACTION_PARSER = 'html.parser'
SCRACHY_CONTENT_EXTRACTION_METHOD = 'basic'
SCRACHY_RESPONSE_RETRIEVAL_METHOD = 'standard'

# Simhash Settings
SCRACHY_USE_SIMHASH = False
SCRACHY_SIMHASH_TOKENIZER = 'space'
SCRACHY_SIMHASH_WINDOW = 4
SCRACHY_SIMHASH_KEEP_PUNCTUATION = False
SCRACHY_SIMHASH_USE_LOWERCASE = True
# I suggest using xxhash64 or spooky64, but they require additional installation.
SCRACHY_SIMHASH_HASH_ALGORITHM = 'sha1'

# Middleware Settings
SCRACHY_IGNORE_EXCLUDE_URL_PATTERNS = [
    r'books\.toscrape\.com/index\.html',
    r'/catalogue/category/books/[hH]',
    r'/catalogue/category/books/[aA]',
    r'page-1\.'
]
SCRACHY_DEFAULT_ENCODING = 'utf-8'

# Regular Scrapy Settings
LOG_ENABLED = True
LOG_LEVEL = 'INFO'
HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = 'scrachy.middleware.httpcache.AlchemyCacheStorage'
DOWNLOADER_MIDDLEWARES = {
    # You probably want this early in the pipeline, because there's no point
    # in the other middleware if its in the cache and we are going to ignore it
    # anyway.
    'scrachy.middleware.ignorecached.IgnoreCachedResponse': 50,

    # Note this has to be after the HttpCacheMiddleware!
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 1000,
}

