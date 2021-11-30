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
# Generic CLI parser framework.
# - ARCLI is the only concrete implementation available.
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

import logging
from .arcli.ArCliParser import ArCliParser
from .arcli.ArCliContext import ArCliContext


# Logger
log = logging.getLogger(__name__)


# Generic parser factory
class CliParserFactory():
    def __init__(self):
        pass

    @staticmethod
    def getParser(parserName, **parserKwArgs):
        arCliContext = ArCliContext()
        arCliContext.loadArCliDocuments(parserKwArgs['arCliConfig'])
        arCliParser = ArCliParser(arCliContext)
        return arCliParser
