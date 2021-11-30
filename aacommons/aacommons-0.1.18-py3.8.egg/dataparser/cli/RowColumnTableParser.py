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
# Row/column table parser.
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
from .GenericJsonCsvTableParser import GenericJsonCsvTableParser
from .GenericRegexTableParser import GenericRegexTableParser
from .RowColumnTableParserAosDpStd import RowColumnTableParserAosDpStd
from .RowColumnTableParserAosStd import RowColumnTableParserAosStd


# Logger
log = logging.getLogger(__name__)


class RowColumnTableParser(AbstractTableParser):
    def __init__(self, source, marker=None, tableOptions=None):
        super().__init__()

        # Pre-process source
        if (tableOptions is not None) and 'begin' in tableOptions:
            tableBegin = tableOptions['begin']
            m_start = re.search(tableBegin, source)
            if m_start is not None:
                source = source[m_start.start():]
                log.debug("table.begin regex: [%s] matched at: [%s]" % (tableBegin, m_start.start()))
            else:
                log.debug("table.begin regex: [%s] did NOT match" % (tableBegin))
        if (tableOptions is not None) and 'end' in tableOptions:
            tableEnd = tableOptions['end']
            m_end = re.search(tableEnd, source)
            if m_end is not None:
                source = source[0:m_end.start()]
                log.debug("table.end regex: [%s] matched at: [%s]" % (tableEnd, m_end.start()))
            else:
                log.debug("table.end regex: [%s] did NOT match" % (tableEnd))
        if log.isEnabledFor(logging.DEBUG):
            # Log beginning and end of source
            b = min(10, len(source))
            e = min(10, len(source))
            log.debug("source.begin: [%s]" % (source[0:b]))
            log.debug("source.end: [%s]" % (source[len(source) - e:]))

        # Find delegate parser
        parserName = "aos-std"
        if tableOptions is not None:
            parserName = tableOptions['parser']
        if parserName == "aos-std":
            # Backwards compatibility, default to standard AOS tables
            self.parser = RowColumnTableParserAosStd(source, marker)

        elif parserName == "aos-dp-std":
            self.parser = RowColumnTableParserAosDpStd(source, marker)

        elif parserName == "generic-regex":
            self.parser = GenericRegexTableParser(source, tableOptions)

        elif parserName == "generic-json-csv":
            self.parser = GenericJsonCsvTableParser(source, tableOptions)

        else:
            raise Exception("unknown table parser: " + parserName)

    def process(self):
        self.parser.process()

    def getTables(self):
        return self.parser.getTables()
