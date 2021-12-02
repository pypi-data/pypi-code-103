#!/usr/bin/env python3
#
# Copyright 2021 Jonathan Lee Komar
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import abc
import os
from typing import Dict
from functionaljlk import getMapValue, IniConfigReader, Result
import logging

class Configuration(abc.ABC):
    """Main configuration abstraction.

       Defines what can be retrieved.

        Example:
        [Targets]
        admin=https://admin.opencast.org
        player=https://player.opencast.org
        worker1=https://worker1.opencast.org
        
        [Security]
        authentication=basic
        username=myuser
        password=mypassword

    """

    # CLASS DEFAULTS
    DEFAULT_PATH='/etc/opencastapi/opencastapi.conf'
    ENV_PATH_KEY='OPENCASTAPI_CONF_PATH'
    TARGETS_SECTION_NAME="Targets"
    SECURITY_SECTION_NAME="Security"
    DEFAULT_HTTP_GET_HEADERS = dict([
        ('Content-Type', 'application/json'),
        ('Accept', 'application/v1.6.0+json'),
        ('X-Requested-Auth', 'Basic'),
        ("Accept-Charset", "UTF-8")
        ])
    DEFAULT_HTTP_POST_HEADERS = dict([])

    def __init__(self):
        """
            Parameters:
            obj: the subclass implementation of this configuration
        """

    def default_headers_for(self, http_verb: str) -> Dict:
        if http_verb.lower() == "get":
            return Configuration.DEFAULT_HTTP_GET_HEADERS

    @abc.abstractmethod
    def target(self, target_id: str) -> str:
        """Getter URL for target id from a map of str -> URL where str is a target_id and URL is a urlparse.ParseResult 
            
            Supports arbitrary number of server urls for Opencast instances.

            Parameters:
            target_id (str): example may be one of [admin, player, worker] whereby the case is sensitive.

            Return:
            target_url (Result[urlparse.ParseResult]): The URL retrieved.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def username(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def password(self):
        raise NotImplementedError

    def _encrypt(self, value) -> str:
        if value is None or len(value) == 0:
            return ""
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key.encode(''), AES.MODE_CFB, iv)

    def _decrypt(self) -> str:
        pass

class EnvironmentThenFileConfiguration(Configuration):
    """The standard runtime implementation for the configuration.

        Priority:
         1. Use path provided.
         2. Use environment variable.
         3. Use default path.
    """
    def __init__(self, path: str=None):
        """Constructor

            Policy: Fail to construct if the configuration is not sufficient.
        """
        super().__init__()
        determined_path = Result.of(path)\
            .orElse(Result.of(os.environ.get(Configuration.ENV_PATH_KEY)))\
            .getOrElse(Configuration.DEFAULT_PATH)
        reader = IniConfigReader(determined_path, f"Consider setting environment variable {Configuration.ENV_PATH_KEY}.") 
        self._target_map = reader.getEntries(section=Configuration.TARGETS_SECTION_NAME)\
            .map(lambda l: dict((a,b) for (a,b) in l))
        self._username = reader.getProperty(section=Configuration.SECURITY_SECTION_NAME, key='username')\
            .getOrElse(lambda: logging.error(f'Config missing {Configuration.SECURITY_SECTION_NAME} section with username key.'))
        self._password = reader.getProperty(section=Configuration.SECURITY_SECTION_NAME, key='password')\
            .getOrElse(lambda: logging.error(f'Config missing {Configuration.SECURITY_SECTION_NAME} section with password key.'))

    def target(self, target_id: str) -> str:
        """

            Parameters:
            target_id (str): The id of the configuration key under the section Configuration.TARGET_SECTION_NAME.

            Return:
            Result.Success[str] if found.
            Result.Failure if not found.
        """
        return self._target_map\
            .flatMap(lambda m: getMapValue(target_id, m)).getOrException()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password


class TestConfiguration(Configuration):
    """The test configuration implementation.
    """
    def __init__(self, port=55000):
        self.port = port

    def target(self, target_id: str):
        return f"http://localhost:{self.port}"
    @property
    def username(self):
        return "testuser"
    @property
    def password(self):
        return "testpassword"
