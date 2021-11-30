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
# ARCLI result.
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

'''
#
# ArCliResult: ARCLI parser result.
#
'''
class ArCliResult():
    # Result types
    TYPE_REGEXES_BYLINE='regexes_byline'
    TYPE_REGEXES_ENTIRE='regexes_entire'
    TYPE_TABLES='tables'

    def __init__(self):
        self._result = {}

    def get(self):
        return self._result

    def addType(self, rtype):
        self._result[rtype] = []

    def addSection(self, rtype, sname=None):
        messages = []
        if sname is None:
            sname = rtype
        resultData = { sname: messages }
        self._result[rtype].append(resultData)
        return messages
