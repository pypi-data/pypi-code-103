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
# ContentProvider
#
# Provides some content through getContent()
#
# Authors: Thomas Bastian, Albert Pang
#
'''

import json
import logging
import os
import time

import requests
import urllib3
from yaml import dump

from .RedisStore import RedisStore
from .util import convertToDict

DEFAULT_API_TIMEOUT = 15  # Default timeout value (s) for APIContentProvider

urllib3.disable_warnings()

# Logger
log = logging.getLogger(__name__)


class ContentProvider():
    def __init__(self):
        pass

    def __str__(self):
        return ""

    def getContent(self):
        return None

    def getContentData(self):
        ''' Attempt to decode the content read and returns a dictionary or a list.
        Will attempt to decode the content as JSON or YAML

        Parameter
        ---------
            None

        Returns
        -------
            dict or list : A dictionary if able to convert content as dict or list. None if unsuccessful
        '''
        content = self.getContent()

        return convertToDict(content)

    def reprJSON(self):
        data = {}
        data['ContentProvider'] = str(self)
        return data

    def getContentJSON(self):
        '''Attempt to return a JSON object from the content source.

        Parameters
        ----------
            None

        Returns
        -------
            str : A JSON object string. Returns None if unable to convert content to JSON object
        '''
        data = self.getContentData()

        if isinstance(data, dict) or isinstance(data, list):
            log.debug("Found dict or list")
            return json.dumps(data)
        else:
            return None

    def getContentYml(self):
        '''Attempt to return a YAML formatted string from the content source.

        Parameters
        ----------
            None

        Returns
        -------
            str : A string in YAML format. Returns None if unable to convert content to JSON object
        '''
        data = self.getContentData()

        if isinstance(data, dict) or isinstance(data, list):
            log.debug("Found dict or list")
            return dump(data)
        else:
            return None

    def __iter__(self):
        return None

    def _next(self):
        raise StopIteration

    def __next__(self):
        return self._next()

    def next(self):
        return self._next()


class FileContentProvider(ContentProvider):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "file://" + self.filename

    def getContent(self):
        fileHandle = open(self.filename, 'r')
        fileContent = fileHandle.read()
        fileHandle.close()
        return fileContent


class MultiFileContentProvider(ContentProvider):
    def __init__(self, dirname, endswith):
        self.dirname = dirname
        self.endswith = endswith
        self.fileIterator = None

    def __str__(self):
        return "dir://" + self.dirname + ", ending with: " + self.endswith

    def __repr__(self):
        return "dir://" + self.dirname + ", ending with: " + self.endswith

    def getContent(self):
        raise "unimplemented"

    def __iter__(self):
        self.fileIterator = iter(os.listdir(self.dirname))
        return self

    def _next(self):
        try:
            while True:
                filename = next(self.fileIterator)
                if filename.endswith(self.endswith):
                    break
            p = os.path.join(self.dirname, filename)
            return FileContentProvider(p)

        except StopIteration:
            raise StopIteration


class RedisStoreContentProvider(ContentProvider):
    def __init__(self, redisUrl, redisKey):
        self.redisUrl = redisUrl
        self.redisKey = redisKey

    def __str__(self):
        return self.redisUrl + "/" + self.redisKey

    def getContent(self):
        r = RedisStore(url=self.redisUrl)
        content = r.get(self.redisKey)
        return content


class MultiKeyRedisStoreContentProvider(ContentProvider):
    def __init__(self, redisUrl, redisKeysPatterns):
        self.redisUrl = redisUrl
        self.redisKeysPattern = redisKeysPatterns

    def __str__(self):
        return self.redisUrl + "/" + self.redisKeysPattern

    def __repr__(self):
        return self.redisUrl + "/" + self.redisKeysPattern

    def getContent(self):
        raise "unimplemented"

    def __iter__(self):
        r = RedisStore(url=self.redisUrl)
        redisKeys = r.keys(pattern=self.redisKeysPattern)
        self.fileIterator = iter(redisKeys)
        return self

    def _next(self):
        try:
            while True:
                redisKey = next(self.fileIterator)
                break
            return RedisStoreContentProvider(self.redisUrl, redisKey)

        except StopIteration:
            raise StopIteration


class ApiContentProvider(ContentProvider):
    def __init__(self, apiUrl, endpoint, params=None, sip_mode=True,
                 verify=True, timeout=DEFAULT_API_TIMEOUT, cache_max_age=0):
        '''Retrieve content using REST API (http GET only)

        Parameters
        ----------
        apiUrl : str
            The host portion of the complete REST API call.
                E.g.
                    https://www.google.com
                    http://localhost:5000
            Trailing '/' is optional
        endpoint : str
            The endpoint of the complete REST API call
                E.g.
                    /endpoint
                    endpoint
            Leading '/' is optional
        params : dict, default=None
            list of tuples or bytes to send in the query string
            Do not set this if you want to use the 'getContentByEndpointParam()'
            method to add parameters dynamically for each call, or un
        sip_mode : bool, default=True
            Legacy behaviour for Aruba SIP. The message contained in JSON object
            is expected to be in the 'msg' attribute. e.g.
                { 'msg': {'a': 'value1', 'b': 'value2'} }
            The value of the 'msg' attribute (i.e. {'a': 'value1', 'b': 'value2'})
            instead of the whole thing.  Set to False to disable this behaviour.
            For backward compatibility in SIP software, this behaviour is enabled
            by default.
            TODO: refactor RR and ND scripts and change default to sip_mode=False
        verify : bool or str, default=True
            Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use.
        timeout : int, default=DEFAULT_API_TIMEOUT
        cache_max_age: int
            cache_max_age is an integer, expressing a number of seconds.
            - If set to a non-zero positive integer, caching is enabled for this
            content-provider. The cache will be consulted before the API call is
            issued to the external source.
            - If cache_max_age is set to a negative
            interger, any cached content will be considered valid until the cache
            is cleared with the clear_cache() method.
            - If cache_max_age == 0, caching is disabled
        '''
        self.apiUrl = apiUrl.rstrip('/') if apiUrl else ""
        self.endpoint = endpoint if endpoint else ""
        self.params = params
        self.sip_mode = sip_mode
        self._verify = verify
        self._timeout = timeout
        if self.endpoint.startswith("/"):
            self._url = self.apiUrl + self.endpoint
        else:
            self._url = self.apiUrl + "/" + self.endpoint
        try:
            self.cache_max_age = int(cache_max_age)
        except TypeError as e:
            log.warning(f"invalid value for 'cache_max_age'={cache_max_age}. Caching disabled. ({e})")
            self.cache_max_age = 0
        self.cache = None  # Cache for the getConteng() calls
        self.param_cache = dict()   # Cache for the getContentByEndpointParam() calls

    def __str__(self):
        return self._url

    def getContent(self):
        cached_response = None
        if self.cache_max_age != 0:
            cached_response = self.from_cache()
        if cached_response is None:
            try:
                if self.params is not None:
                    response = requests.request("GET", self._url,
                                                params=self.params, verify=self._verify,
                                                timeout=self._timeout)
                else:
                    response = requests.request("GET", self._url,
                                                verify=self._verify,
                                                timeout=self._timeout)
                self.update_cache(response)
            except Exception as e:
                log.error(f"Cannot retrieve content from {str(self)} ({e})")
                return ""   # TODO: this should really be None
        else:
            response = cached_response
        try:
            if self.sip_mode:
                # NOTE: the 'msg' is for SIP backward-compatibility
                return json.dumps(response.json()['msg'])
            else:
                return json.dumps(response.json())
        except Exception as e:
            log.error(f"Cannot retrieve content from {str(self)} ({e})")
            return ""

    def getContentByEndpointParam(self, param=None):
        '''
        Similar to getContent(), instead of passing the parameters in the form or URL query string
        such as:
            /url/endpoint?key1=value1&key2=value2
        pass the single parameter as a suffix of the URL

            /url/endpoint/param
        '''
        cached_response = None
        if self.cache_max_age != 0:
            cached_response = self.from_cache(param=param)
        if cached_response is None:
            try:
                if param:
                    if param.startswith("/"):
                        url = self._url + param
                    else:
                        url = self._url + "/" + param
                    response = requests.request("GET", url, verify=self._verify,
                                                timeout=self._timeout)
                else:
                    response = requests.request("GET", self._url,
                                                verify=self._verify, timeout=self._timeout)
                self.update_cache(response, param=param)
            except Exception as e:
                log.error(f"Cannot retrieve content from {str(self)}/{param} ({e})")
                return ""   # TODO: Should really be None
        else:
            response = cached_response
        try:
            # NOTE: the 'msg' is for SIP backward-compatibility
            if self.sip_mode:
                return json.dumps(response.json()['msg'])
            else:
                return json.dumps(response.json())
        except Exception as e:
            log.error(f"Cannot retrieve content from {str(self)}/{param} ({e})")
            return ""

    def getContentByEndpointParamData(self, param=None):
        ''' Similar to getContentByEndpointParam(), except attempt to convert
        retrieved content to dict
        '''

        content = self.getContentByEndpointParam(param=param)

        return convertToDict(content)

    def update_cache(self, content, param=None):
        ''' Update cache with content

        Parameter
        ---------
        content: Object
            any content that can be cached
        param: str
            A parameter string
                for self.getContent() this is None
                for self.getContentByEndpointParam(), this is the parameter to be passed into the call
        '''
        log.debug("update cache")
        data = dict()
        data['timestamp'] = int(time.time())
        data['content'] = content

        if param is None:
            self.cache = data
        else:
            self.param_cache[param] = data

    def from_cache(self, param=None):
        ''' Retrieve content from cache.  Returns None if cache missed or cache expired
        '''
        if self.cache_max_age == 0:
            log.debug("caching disable")
            return None
        if param is None:
            cache = self.cache
        else:
            cache = self.param_cache.get(param, None)
        if cache is None:
            log.debug("cache miss")
            return None

        now = int(time.time())
        cache_timestamp = cache['timestamp']
        cache_content = cache['content']

        if self.cache_max_age < 0:
            return cache_content
        if now - cache_timestamp >= self.cache_max_age:
            # cache expired
            log.debug("cache expire")
            return None
        else:
            log.debug("cache hit")
            return cache_content

    def clear_cache(self):
        ''' Clear the cache (for all parameters)
        '''
        self.cache = None
        self.param_cache = dict()
