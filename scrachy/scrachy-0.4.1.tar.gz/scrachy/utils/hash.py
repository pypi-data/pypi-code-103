##############################################################################
#  Copyright 2020 Reid Swanson and the Scrapy developers.
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

##############################################################################
#
#   For code derived from the Scrapy developers you must also follow the
#   terms set by the 3-Clause BSD license. See the BSD_LICENSE.md file or
#   online at <https://opensource.org/licenses/BSD-3-Clause>.
#
##############################################################################

# Python Modules
import hashlib

# 3rd Party Modules
import scrapy
import w3lib.url

from scrapy.utils.python import to_bytes

try:
    import spookyhash
except ImportError:
    spookyhash = None

try:
    import xxhash
except ImportError:
    xxhash = None

# Project Modules


make_hasher = {
    'md5': lambda: hashlib.md5(),
    'sha1': lambda: hashlib.sha1(),
    'spooky32': lambda: spookyhash.Hash32(),
    'spooky64': lambda: spookyhash.Hash64(),
    'spooky128': lambda: spookyhash.Hash128(),
    'xxhash32': lambda: xxhash.xxh32(),
    'xxhash64': lambda: xxhash.xxh3_64(),
    'xxhash128': lambda: xxhash.xxh3_128(),
}
"""
A dictionary that maps a known hash algorithm name to a function that
constructs an instance of that algorithm.
"""


def request_fingerprint(request: scrapy.http.Request, hash_fn) -> bytes:
    """
    Similar to :func:`scrapy.utils.request.request_fingerprint` but uses a
    configurable hash algorithm and always ignores headers and fragments. It
    also returns an object of type ``bytes``, instead of a hex string.

    :param request: The :class:`scrapy.http.Request` to fingerprint.
    :param hash_fn: A hash function object that adheres to the hashlib API. Namely, it
           must have an ``update`` function and a ``digest`` function.
    :return: The digest as an array of bytes.

    :raises KeyError: if the ``hash_name`` is unknown.
    """
    # This code has been adapted directly from Scrapy.
    hash_fn.update(to_bytes(request.method))
    hash_fn.update(to_bytes(w3lib.url.canonicalize_url(request.url)))
    hash_fn.update(to_bytes(request.body or b''))

    return hash_fn.digest()


def hash_text(s: str, hash_fn) -> bytes:
    """
    Hash a string of text using the specified hash algorithm.

    :param s: The string to hash.
    :param hash_fn: A hash function object that adheres to the hashlib API.
           Namely, it must have an ``update`` function and a ``digest``
           function. In practice it should be created using the
           :data:`.make_hasher` dictionary.
    :return: The hash digest as an array of bytes.

    """
    hash_fn.update(to_bytes(s or b''))

    return hash_fn.digest()
