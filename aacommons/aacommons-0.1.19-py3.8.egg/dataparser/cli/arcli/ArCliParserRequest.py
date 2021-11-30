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
# ArCliParserRequest
#
# Authors: Thomas Bastian
#
'''

'''
# Parameters
'''
'''
#
'''

import logging
from ..CliParserBase import CliParserRequest


# Logger
log = logging.getLogger(__name__)


'''
#
# ArCliParserRequest: ARCLI parser request.
#
# MANDATORY fields
# - Source: <string> <source>
# - Command: <string> <CLI command>
# - Stdout: <string> <CLI output to parse>
# - Label: <string> <<device class>/<qualifier>>
# - LocalBeginTime: <float> <timestamp>
#
# OPTIONAL fields
# - Status: <int> <when < 0 parser will not process request>
# - ContentType: <string> <text/plain, application/json, etc...>
# - Origin: <string or dict> <origin tags>
#
'''
class ArCliParserRequest(CliParserRequest):
    def __init__(self):
        super().__init__()

    # Hook to provide additional output tags
    # Return None or a dictionary
    def getOutputTags(self, arCliContext, source):
        log.debug("arCliContext: %s, source: %s" % (arCliContext, source))
        outputTags = arCliContext.getOriginTags(self.get('Origin', None), source)
        return outputTags

    # Hook to provide additional body tags
    # MUST return a dictionary
    def getBodyTags(self, arCliContext, source):
        log.debug("arCliContext: %s, source: %s" % (arCliContext, source))
        return dict()

    # Hook for document processing
    # MUST return True to keep processing or False to stop processing
    def processDocument(self, arCliContext, source, cliCommandDef):
        document = cliCommandDef['document']
        group = cliCommandDef['group']
        log.debug("arCliContext: %s, source: %s, document: %s, group: %s" % (arCliContext, source, document, group))
        return True

    # Hook to process posted message (i.e. modify body and output)
    # MUST return array of (document, output) to post message(s) or None to discard message
    def updateMessageTags(self, arCliContext, source, document, output):
        log.debug("arCliContext: %s, source: %s, document: %s, output: %s" % (arCliContext, source, document, output))
        return [(document, output)]
