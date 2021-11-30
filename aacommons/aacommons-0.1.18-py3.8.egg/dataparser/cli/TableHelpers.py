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
# Helpers for parsing table data out of text.
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
from .RowColumnTableParser import RowColumnTableParser


# Logger
log = logging.getLogger(__name__)


'''
All parsing is configured via table options.

TABLE OPTIONS
-------------
Dictionary that contains common table options and parser specific table options.
The table parser MUST always be specified.

{
   "parser": "aos-std|aos-dp-std|generic-regex|generic-json-csv"
   [, "begin": "<begin>" ]
   [, "data.trim": false|true ]
   [, "end": "<end>" ]
   [, "json.lines": "<key>" ]
   [, "marker": "<marker>" ]
   [, <parser specific table options> ]
}

TABLE PARSERS
-------------
Following table parsers are available (key 'parser'):
- "aos-std": understands standard AOS table output such as "show ap active",
             "show user", "show ap bss-table", etc...
- "aos-dp-std": understands standard AOS datapath table output such as
                "show datapath tunnel table", etc...
- "generic-regex": generic regular expression based table parser.
- "generic-json-csv": generic JSON CSV like output table parser.

COMMOM TABLE OPTIONS
--------------------
All parsers will honor following optional parameters:
- "begin": "<begin regex>". Defines a regular expression that will mark the
           beginning of the CLI output to use for parsing the table. This will
           typically be needed when the CLI output holds several tables.
           Default: None
           NOTE: when the provided <begin regex> does not match, the result will
                 be like no <begin regex> was provided.
- "end": "<end regex>". Defines a regular expression that will mark the end
         of the CLI output to use for parsing the table. This will typically be
         needed when the table has trailing output that is not part of the table.
         Default: None
         NOTE: when the provided <end regex> does not match, the result will
               be like no <end regex> was provided.
               The provided <end regex> applies to CLI output AFTER <begin regex>
               has matched or if no <begin regex> was provided to beginning of CLI
               output.
- "marker": "<marker>". Provide table marker, such as "Active AP Table" for table "show ap active".
            Default None, which auto-detects the marker based on the first lines of output.
- "json.lines": "<key>". By default input is assumed to be text. When "json.lines" is specified, input is expected
                to be a JSON object where the "json.lines" provided key specifies an array of text lines, such as:
                { "_data": [ "line1", "line2", "line3" ] } (i.e. "json.lines": "_data")
                Default: None
- "data.trim": true|false. When true, all table values have beginning and ending white-spaces trimmed.
               Default: true

aos-std TABLE PARSER OPTIONS
----------------------------
None in addition to the common table parser parameters.

aos-dp-std TABLE PARSER OPTIONS
-------------------------------
None in addition to the common table parser parameters.

generic-regex TABLE PARSER OPTIONS
----------------------------------
The generic regular expression based parser supports three broad use cases:
- header driven split-up based on spacing between column names, specify:
  "header.offset" and "data.offset" parameters and optionally "stop.on.empty.line".
- header driven split-up based on regex with named groups, specify:
  "header.offset", "header.regex" and "data.offset" parameters and optionally
  "stop.on.empty.line".
- data driven split-up based on regex with named groups, specify:
  "data.offset" and "data.regex" parameters and optionally "stop.on.empty.line" and/or
  "skip.partial.match".

Parameter details:
NOTE: all offsets are relative to the FIRST non blank line in CLI output, i.e. offset
      0 is the first non blank line.
"header.offset": sets the relative offset of the header line.
"header.regex": sets the regular expression to be used to break-up the header line.
"data.offset": sets the relative offset of the first data line
"data.regex": sets the regular expression to be used to break-up each data line.
"stop.on.empty.line": true or false, defaults to true. When true, parsers stops on first
                      blank/empty line.
"skip.partial.match": true or false, defaults to false. When true, parser ignores data lines
                      that don't match the data regular expression.

generic-json-csv TABLE PARSER OPTIONS
-------------------------------------
None in addition to the common table parser parameters.

'''


'''
#
# Parse content as list of dictionaries
#
'''
def contentAsListOfDict(content, marker=None, headerList=None, tableOptions=None):
    if tableOptions is not None:
        marker = tableOptions.get('marker', marker)
    if tableOptions is not None and 'json.lines' in tableOptions:
        # Lines are already in an array
        source = content[tableOptions['json.lines']]
    else:
        # Assume text
        source = content
    parser = RowColumnTableParser(source, marker=marker, tableOptions=tableOptions)
    parser.process()
    parsedTable = parser.getTables()[0]
    # Data trim, default true
    if (tableOptions is None) or ('data.trim' in tableOptions and tableOptions['data.trim']) or ('data.trim' not in tableOptions):
        # Header
        for header in parsedTable['header']:
            header['title'] = header['title'].strip()
        # Data
        for row in parsedTable['rows']:
            i = 0
            for value in row:
                row[i] = value.strip()
                i += 1
    return tableAsListOfDict(parsedTable, headerList=headerList)


'''
#
# Parse content as parameter value list
#
'''
def contentAsParameterValueList(content, marker=None):
    source = content
    parser = RowColumnTableParser(source, marker=marker)
    parser.process()
    parsedTable = parser.getTables()[0]
    # Data
    parameterValueList = dict()
    for row in parsedTable['rows']:
        parameterValueList[row[0].strip()] = row[1].strip()
    return parameterValueList


'''
#
# Table as list of dictionaries
#
'''
def tableAsListOfDict(table, headerList=None):
    # Fill list
    trows = table['rows']
    theader = table['header']
    valueList = []
    if headerList is not None:
        for cheader in theader:
            headerList.append(cheader['title'])
    for row in trows:
        rowd = dict()
        for c in range(0, len(row)):
            rowd[theader[c]['title']] = row[c]
        valueList.append(rowd)
    return valueList
