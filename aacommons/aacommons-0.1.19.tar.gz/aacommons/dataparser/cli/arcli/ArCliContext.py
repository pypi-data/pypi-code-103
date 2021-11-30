#
# Copyright 2021 Thomas Bastian, Jeffrey Goff, Albert Pang
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
# ARCLI parser context.
#
# Authors: Thomas Bastian, Jeff Goff
#
'''

'''
# Parameters
'''
'''
#
'''

import base64
import logging
from .ArCliDocuments import ArCliDocuments
from json import loads


# Logger
log = logging.getLogger(__name__)


# Default field name separator
ND_FIELD_NAME_SEPARATOR='.'


'''
#
# ArCliContext: ARCLI parser context.
#
'''
class ArCliContext:
    def __init__(self):
        self.arCliDocuments = None
        self.options = None
        self.origin = None
        self.originTagCache = { }
        self.originTagCacheBySource = { }

    def getArCliDocumentsByLabel(self, label):
        # First lookup by exact label
        arCliDocuments = self.arCliDocuments.getByLabel(label)
        if arCliDocuments is None:
            # Fallback to <device class>/default
            _label = label.split("/")[0] + "/default"
            arCliDocuments = self.arCliDocuments.getByLabel(_label)
            if arCliDocuments is None:
                # Fallback to default/default
                arCliDocuments = self.arCliDocuments.getByLabel("default/default")
        return arCliDocuments

    def loadArCliDocuments(self, contentProvider):
        self.arCliDocuments = ArCliDocuments(contentProvider, ND_FIELD_NAME_SEPARATOR)

    def getArCliMappings(self):
        return self.arCliDocuments.getMappings()

    # Set options
    def setOptions(self, options):
        self.options = options

    # Get options
    def getOptions(self):
        return self.options

    def setOrigin(self, origin):
        '''Set origin value. Supports:
        1. A dict
        2. A string that contains a list of comma separated key-value pairs:
           key1=value1[,key2=value]
        3. A base64 encoded JSON string
        '''
        self.origin = origin
        self.originTagCache = {}
        self.originTagCacheBySource = {}

    def getOrigin(self):
        return self.origin

    def _getOriginTags(self, origin):
        # Retrieve cached tags for a given origin object
        # Supported origin objects:
        # - dict object
        # - base64 encoded JSON
        # - "key1=value1[,key2=value]"
        if origin is None:
            return None
        if isinstance(origin, dict):
            # Dict are not hashable, hence cannot cache
            return origin
        tags = self.originTagCache.get(origin, None)
        if tags is None:
            ck = origin
            if isinstance(origin, str) or isinstance(origin, unicode):
                # base64 encoded JSON or "key1=value1[,key2=value]"
                if (len(origin) % 4) == 0:
                    # Possibly base64 encoded JSON
                    try:
                        _origin = base64.b64decode(origin)
                        origin = loads(_origin)
                    except TypeError:
                        log.debug('base64 decode failed: %s' % (origin))
                    except Exception:
                        log.error('origin: [%s] not JSON' % (_origin))
            if isinstance(origin, dict):
                tags = {}
                for k in origin.keys():
                    tags[k] = origin[k]
                self.originTagCache[ck] = tags
            elif isinstance(origin, str) or isinstance(origin, unicode):
                tags = {}
                kvps = origin.split(',')
                for _kvp in kvps:
                    kvp = _kvp.split('=', 1)
                    tags[kvp[0]] = kvp[1]
                self.originTagCache[ck] = tags
            else:
                raise Exception('unsupported origin type: ' + str(type(origin)))
        return tags

    def getOriginTags(self, origin, source):
        # Retrieve cached tags for a given origin object and source
        # Supported origin objects:
        # - dict object
        # - base64 encoded JSON
        # - "key1=value1[,key2=value]"
        # Origin object can be either:
        # - flat: { "customerid": "customerid" }
        # - keyed by source: { "<source1>": { "customerid": "customerid" }, ... }
        if origin is None:
            return None
        if source is None:
            # Must resolve based on source
            raise Exception("source is None")
        tags = self.originTagCacheBySource.get(source, None)
        if tags is None:
            # Get tags from origin
            otags = self._getOriginTags(origin)
            tags = {}
            if source in otags:
                # Keyed by source
                otags = otags[source]
            elif 'default' in otags:
                otags = otags['default']
            for k in otags.keys():
                if k.startswith('nd.origin.'):
                    tags[k] = otags[k]
                else:
                    if not isinstance(otags[k], dict):
                        tags['nd.origin.' + k] = otags[k]
            self.originTagCacheBySource[source] = tags
        if len(tags) == 0:
            return None
        return tags
