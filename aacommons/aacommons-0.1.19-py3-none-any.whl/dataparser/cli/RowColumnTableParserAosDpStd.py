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
# Standard AOS datapath row/column table parser.
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
import re
from .AbstractTableParser import AbstractTableParser


# Logger
log = logging.getLogger(__name__)


class RowColumnTableParserAosDpStd(AbstractTableParser):
    def __init__(self, source, marker=None):
        super().__init__()
        self.source = source
        self.marker = marker

    def readContent(self):
        if type(self.source) == list:
            self.contentLines = self.source
        else:
            self.contentLines = self.source.splitlines()

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
            column = { 'begin': begin, 'end': i, 'title': header[begin:min(i, len(header))] }
            page.append(column)
            begin = i
        return page

    def parse(self):
        # Process structure
        log.debug("marker [%s]" % str(self.marker))
        if self.marker is None:
            # No marker was given, find out from first 10 lines
            currentLineNo = 0
            for currentLine in self.contentLines:
                if currentLineNo > 10:
                    break
                if len(currentLine) > 0 and ((currentLineNo + 1) < len(self.contentLines)):
                    nextLine = self.contentLines[currentLineNo + 1]
                    if (re.match("\\-+", nextLine) is not None) and (len(currentLine) == len(nextLine)):
                        # Got marker
                        self.marker = currentLine
                        log.debug("got marker [%s]" % str(self.marker))
                        break
                currentLineNo += 1
            if self.marker is None:
                raise Exception()

        # Update main table
        self.tables[0]['name'] = self.marker
        log.debug("processing table [%s]" % str(self.marker))

        markerLine = -1
        currentPage = None
        currentLineNo = 0
        rows = []
        for currentLine in self.contentLines:
            # Begin page
            if currentLine.startswith(self.marker):
                log.debug("begin page [%s] at [%d]" % (str(self.marker), currentLineNo))
                markerLine = currentLineNo
                currentPage = None
                currentLineNo += 1
                continue

            if (len(currentLine.strip()) == 0) and (currentPage is not None):
                # Ignore empty lines
                currentLineNo += 1
                continue

            # Skip information content between begin page and actual data
            if (currentPage is None) and (markerLine >= 0) and (currentLineNo > (markerLine + 2)):
                if currentLine.startswith("-"):
                    currentPage = self.createPage(self.tables[0],
                                                  self.contentLines[currentLineNo],
                                                  self.contentLines[currentLineNo - 1])
                    log.debug("new page [%s] at [%d]" % (currentPage, currentLineNo))
                    if not 'header' in self.tables[0]:
                        self.tables[0]['header'] = currentPage
                    currentLineNo += 1
                    continue

            if (currentPage is not None) and (currentLineNo > (markerLine + 3)):
                row = self.createRow(currentLine, currentPage)
                log.debug("new row [%s] at [%d]" % (row, currentLineNo))
                rows.append(row)

            currentLineNo += 1

        self.tables[0]['rows'] = rows
