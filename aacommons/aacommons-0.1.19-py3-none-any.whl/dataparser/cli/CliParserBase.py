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
# CliParser base classes
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
from collections import UserDict


# Logger
log = logging.getLogger(__name__)


# Generic Parser Request
class CliParserRequest(UserDict):
    def __init__(self):
        super().__init__()

    # Hook to clone
    def clone(self):
        c = self.__class__()
        c.update(self)
        return c


# Generic interface for all parsers
class CliParser():
    def __init__(self):
        pass

    def parse(self, parserRequest):
        return None
