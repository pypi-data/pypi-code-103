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
# Abstract table parser.
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


# Logger
log = logging.getLogger(__name__)


class AbstractTableParser():
    def __init__(self):
        self.tables = [{}]
        self.contentLines = []

    def process(self):
        self.preProcess()
        self.readContent()
        self.parse()
        self.postProcess()

    def preProcess(self):
        pass

    def readContent(self):
        pass

    def parse(self):
        pass

    def postProcess(self):
        pass

    def getTables(self):
        return self.tables

    def createPage(self, table, line, header):
        log.debug("table: [%s], line: [%s], header: [%s]" % (table, line, header))
        page = []
        begin = 0
        i = 0
        while i < len(line):
            while (i < len(line)) and (line[i] == '-'):
                i += 1
                continue
            while (i < len(line)) and (line[i] == ' '):
                i += 1
                continue
            column = { 'begin': begin, 'end': i, 'title': header[begin:i] }
            page.append(column)
            begin = i
        return page

    def createRow(self, current, currentPage):
        row = []
        columnNo = 1
        columnCount = len(currentPage)
        for headerColumn in currentPage:
            try:
                beginIndex = headerColumn['begin']
                endIndex = headerColumn['end']
                clen = len(current)
                if clen <= beginIndex:
                    # Not enough characters, generate empty string
                    endIndex = beginIndex = 0
                elif clen <= endIndex:
                    # Not enough characters for this column
                    endIndex = clen
                else:
                    if columnNo == columnCount:
                        # Last column eats everything up
                        endIndex = clen
                row.append(current[beginIndex:endIndex])
            except Exception as e:
                raise Exception(e)
            columnNo += 1
        return row
