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
# Implements a generic table CLI output parser for JSON CSV like output.
# (a JSON array with a header row followed by data rows, each row encoded as a JSON array)
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

import json
import logging
from .AbstractTableParser import AbstractTableParser


# Logger
log = logging.getLogger(__name__)


class GenericJsonCsvTableParser(AbstractTableParser):

    def __init__(self, source, tableOptions={}):
        super().__init__()
        self.source = source

    def readContent(self):
        # TODO: check if jsonData is an array
        self.tableData = json.loads(self.source)

    def parse(self):
        tsize = len(self.tableData)
        log.debug("json table size: [%d]" % (tsize))
        if tsize <= 1:
            # No data
            return

        # Process header
        theader = self.tableData[0]
        hsize = len(theader)
        log.debug("json table header size: [%d]" % (hsize))
        if hsize <= 0:
            # No columns
            return
        columns = []
        for hdata in theader:
            column = { 'title': hdata, 'begin': -1, 'end': -1 }
            columns.append(column)
            log.debug("json table header column: [%s]" % (column['title']))

        # Main table
        self.getTables()[0]['name'] = "generic json csv table"
        rows = []
        self.tables[0]['rows'] = rows
        self.tables[0]['header'] = columns

        # Process rows
        for i in range(1, tsize):
            trow = self.tableData[i]
            rows.append(trow)
            log.debug("json table data row: [%d] [%s]" % (i, str(trow)))
