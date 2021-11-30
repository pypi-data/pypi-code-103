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
# ARCLI sample runner.
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

import logging.config
import sys
import time
from aacommons.contentprovider.ContentProvider import FileContentProvider
from aacommons.dataparser.cli.CliParser import CliParserFactory
from aacommons.dataparser.cli.arcli.ArCliParserRequest import ArCliParserRequest


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-.1s <%(module)s> %(funcName)s | %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout', # Default is stderr
        },
        'debug': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "arcli-parser.log",
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10
        }
    },
    'loggers': {
        'aacommons': { 
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': False
        }
    } 
}
logging.config.dictConfig(LOGGING_CONFIG)


def printResultDataRecord(record):
    n = list(record.keys())[0]
    d = record[n]
    for dr in d:
        (doc, value) = dr
        print(n, doc, value)


def printResultDataRecords(records, f):
    for record in records:
        f(record)


def printResultData(rd):
    if 'regexes_entire' in rd:
        printResultDataRecords(rd['regexes_entire'], printResultDataRecord)
    if 'tables' in rd:
        printResultDataRecords(rd['tables'], printResultDataRecord)
    if 'regexes_byline' in rd:
        printResultDataRecords(rd['regexes_byline'], printResultDataRecord)


def printResult(r, indent):
    (command, resultData) = r
    if isinstance(resultData, dict) or resultData is None:
        # Terminal node
        print(indent, command, "->", str(resultData)[0:60], "...", str(resultData)[-40:])
        if resultData is not None:
            printResultData(resultData)
    elif isinstance(resultData, list):
        print(indent, command)
        for rd in resultData:
            printResult(rd, indent + "  ")
    else:
        raise Exception("not a tuple or list")


def main():
    # Instantiate parser
    contentProvider = FileContentProvider(sys.argv[1])
    cliParser = CliParserFactory.getParser("ARCLI", arCliConfig=contentProvider)

    # Load content
    f = open(sys.argv[4], 'r')
    content = f.read()
    f.close()

    # Parse
    parserRequest = ArCliParserRequest()
    parserRequest['Source'] = "me"
    parserRequest['Command'] = sys.argv[3]
    parserRequest['Stdout'] = content
    parserRequest['Label'] = sys.argv[2]
    parserRequest["LocalBeginTime"] = time.time()
    r = cliParser.parse(parserRequest)

    # Print results
    if r is None:
        print("NO RESULT")
    elif isinstance(r, tuple):
        printResult(r, "")
    else:
        print("UNEXPECTED RESULT")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("%s: <arcli.json> <label> <command> <content>" % (sys.argv[0]))
        sys.exit(1)
    main()
