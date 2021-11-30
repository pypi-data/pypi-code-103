#
# Copyright 2020 Thomas Bastian, Jeffrey Goff, Albert Pang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

'''
#
# RedisStore
#
# A python class for managing the data stored in the redis database.
#
# Authors: Albert Pang
#
'''
# pylint: disable=invalid-name

import json
import jstyleson
import logging
from redis import StrictRedis
from redis.exceptions import ConnectionError, TimeoutError

# Logger
log = logging.getLogger(__name__)


DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0
DEFAULT_REDIS_TIMEOUT = 3  # Normal connection should be very very fast.


class RedisStore(object):
    """A class for managing data in a redis server"""
    def __init__(self, host=DEFAULT_REDIS_HOST, port=DEFAULT_REDIS_PORT,
                 db=DEFAULT_REDIS_DB, url=None, log=None):
        '''
        Parameters
        ----------
        host : str
            Redis host
        port : int
            Redis port
        db : int
            Redis DB number (typically = 0)
        url : str
            Supported format:
            redis://[[username]:[password]]@localhost:6379/0
            rediss://[[username]:[password]]@localhost:6379/0
            unix://[[username]:[password]]@/path/to/socket.sock?db=0

            if url is specified, the other 3 parameters will be ignored
        '''
        super(RedisStore, self).__init__()
        self._log = log
        if url:
            self._store = StrictRedis().from_url(url, socket_connect_timeout=DEFAULT_REDIS_TIMEOUT)
        else:
            self._store = StrictRedis(host=host, port=port, db=db,
                                      socket_connect_timeout=DEFAULT_REDIS_TIMEOUT)
        try:
            self.ping()
        except (ConnectionError, TimeoutError) as e:
            if url:
                url_str = url
            else:
                url_str = "redis://{}:{}/{}. {}".format(host, port, db, e)
            self._log.critical("Cannot connect to Redis server at: %s. Error: %s" % (url_str, e))

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        '''Set the value at key ``name`` to ``value`
        ex: sets an expire flag on key ``name`` for ``ex`` seconds.
        px: sets an expire flag on key ``name`` for ``px`` milliseconds.

        nx: if set to True, set the value at key ``name`` to ``value`` only
          if it does not exist. (i.e. noclobber)

        xx: if set to True, set the value at key ``name`` to ``value`` only
          if it already exists.
        '''
        return self._store.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, name):
        '''Return the value at key ``name``, or "" if the key doesn't exist'''
        value = self._store.get(name)
        if value:
            return value.decode('utf-8')
        else:
            return ""

    def delete(self, name):
        '''delete a key'''
        return self._store.delete(name)

    def exists(self, key):
        '''return True if key exist. False otherwise'''
        return self._store.exists(key)

    def ping(self):
        '''ping the server'''
        return self._store.ping()

    def store_file(self, key, filename, ex=None, px=None, nx=False, xx=False):
        '''stores the entire un-processed content of filename as value into key'''
        try:
            filecontent = open(filename, 'r').read()
        except (FileNotFoundError, PermissionError) as e:
            self._log.error("Cannot open %s for reading. %s" % (filename, e))
            return None
        return self.set(key, filecontent, ex=ex, px=px, nx=nx, xx=xx)

    def store_json_file(self, key, json_file, ex=None, px=None, nx=False, xx=False):
        '''stores the content of json_file as volue into key.
        Attempt to decode the content as JSON before store.
        '''
        try:
            filecontent = open(json_file, 'r').read()
        except (FileNotFoundError, PermissionError) as e:
            self._log.error("Cannot open %s for reading. %s" % (json_file, e))
            return None
        try:
            data = jstyleson.loads(filecontent)
        except ValueError as e:
            self._log.error("Cannot load %s as json object. File not in json format (%s)" % (json_file, e))
            return None
        return self.set(key, json.dumps(data))

    def keys(self, pattern='*'):
        '''Return all keys of the redis server'''
        return self._store.keys(pattern)

    @property
    def dbsize(self):
        '''returns the number of keys in db'''
        return self._store.dbsize()


if __name__ == '__main__':
    pass
