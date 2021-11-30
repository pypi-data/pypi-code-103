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
# Implements a generic table CLI output parser.
#
# All offset are measured relative to the first non blank line in the input.
#
# Three use-cases are handled:
# - header driven split-up based on regex with named groups
# - header driven split-up based on spacing between column names
# - data driven split-up based on regex with named groups
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


class GenericRegexTableParser(AbstractTableParser):
    def __init__(self, source, tableOptions={}):
        super().__init__()
        self.source = source
        self.headerOffset = tableOptions.get("header.offset", -1)
        self.headerRegex = tableOptions.get("header.regex", None)
        self.dataOffset = tableOptions.get("data.offset", -1)
        self.dataRegex = tableOptions.get("data.regex", None)
        self.stopOnEmptyLine = tableOptions.get("stop.on.empty.line", True)
        self.skipPartialMatch = tableOptions.get("skip.partial.match", False)

    def readContent(self):
        if type(self.source) == list:
            self.contentLines = self.source
        else:
            # Sometimes multiple spurious \r are seen before real \r\n
            self.contentLines = re.sub(r"\r+\n", "\n", self.source).splitlines()

    def parse(self):
        # Loop until find first non blank line => reference, i.e. offset 0
        currentLineNo = 0
        while currentLineNo < len(self.contentLines):
            if self.contentLines[currentLineNo].strip() != "":
                break
            currentLineNo += 1

        columns = None
        pattern = None

        if (self.headerOffset >= 0) and ((currentLineNo + self.headerOffset) < len(self.contentLines)):
            # Create named positional columns, data lines chopped based begin/end
            headerLine = self.contentLines[currentLineNo + self.headerOffset]

            if self.headerRegex is not None:
                # Create named positional columns, data lines chopped based begin/end
                columns = self.createPositionalColumnsFromPattern(self.headerRegex, headerLine)
            else:
                # Create positional columns, data lines chopped based begin/end
                columns = self.createPositionalColumnsFromSplit(" +", headerLine)

        else:
            # Create named columns, data lines chopped based on pattern
            pattern = re.compile(self.dataRegex)
            columns = self.createColumnsFromPattern(pattern)

        # Main table
        self.getTables()[0]['name'] = "generic regex table"
        rows = []
        self.tables[0]['rows'] = rows
        self.tables[0]['header'] = columns

        # Read data
        if self.dataOffset < 0:
            return

        currentLineNo += self.dataOffset
        while currentLineNo < len(self.contentLines):
            currentLine = self.contentLines[currentLineNo]
            if currentLine.strip() == "":
                if self.stopOnEmptyLine:
                    break
                else:
                    currentLineNo += 1
                    continue

            if self.headerOffset >= 0:
                # Header based positional break-up
                dataRow = []
                for column in columns:
                    value = ""
                    begin = column['begin']
                    if begin < 0:
                        # Should never happen
                        begin = 0
                    end = column.get('end', -1)
                    if end < 0:
                        # Unset end means until end of line
                        end = len(currentLine)
                    if begin < len(currentLine):
                        value = currentLine[begin:min(end, len(currentLine))]
                    dataRow.append(value)
                rows.append(dataRow)

            else:
                # Data pattern based break-up
                matcher = pattern.match(currentLine)
                matched = matcher is not None
                if not matched and self.skipPartialMatch:
                    currentLineNo += 1
                    continue

                dataRow = []
                groupCount = len(matcher.groups()) if matched else 0
                for column in columns:
                    groupId = column['#']
                    value = ""
                    if groupId >= 1 and groupId <= groupCount:
                        value = matcher.group(groupId)
                        if value is None:
                            value = ""
                    dataRow.append(value)
                rows.append(dataRow)

            currentLineNo += 1

    def createColumnsFromPattern(self, pattern):
        columns = []
        groupIndex = pattern.groupindex
        for namedGroup, groupIndex in sorted(groupIndex.items(), key=lambda x: x[1]):
            column = { 'title': namedGroup, '#': groupIndex }
            columns.append(column)
        return columns

    def createPositionalColumnsFromPattern(self, regex, line):
        pattern = re.compile(regex)
        groupNameByGroupIndex = { }
        for g, i in pattern.groupindex.items():
            groupNameByGroupIndex[i] = g
        matcher = pattern.match(line)
        matched = matcher is not None
        if matched:
            columns = []
            c = 1
            groups = matcher.groups()
            for _ in groups:
                namedGroup = groupNameByGroupIndex.get(c, None)
                if namedGroup is not None:
                    column = { 'title': namedGroup, 'begin': matcher.start(c) }
                    if c < len(groups):
                        # Not last column
                        column['end'] = matcher.end(c)
                    columns.append(column)
                c += 1
            return columns
        else:
            raise Exception("[" + line + "]: does not match regex: [" + regex + "]")

    def createPositionalColumnsFromSplit(self, splitRegex, line):
        splits = re.split(splitRegex, line)
        columns = []
        i = 0
        for split in splits:
            column = { 'title': split, 'begin': line.index(split) }
            if (i + 1) < len(splits):
                # Not last column
                column['end'] = line.index(splits[i + 1])
            columns.append(column)
            i += 1
        return columns
