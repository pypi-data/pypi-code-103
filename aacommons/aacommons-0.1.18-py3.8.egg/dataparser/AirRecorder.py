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
# AirRecorder utilities.
#
# Authors: Thomas Bastian
#
'''

import logging
import time


log = logging.getLogger(__name__)


class Query():
    '''Python variant of AirRecorder Query.
    '''
    def __init__(self, command):
        self.command = command
        # Optional list of sub-queries
        self.subQueries = None
        # Optional {tag, value} pairs
        self.tags = None

    def setCommand(self, command):
        self.command = command

    def getCommand(self):
        return self.command

    def addSubQuery(self, subQuery):
        if self.subQueries is None:
            self.subQueries = []
        self.subQueries.append(subQuery)

    def getSubQueries(self):
        return self.subQueries

    def setTags(self, tags):
        self.tags = tags

    def getTags(self):
        return self.tags

    def addTag(self, tag, value):
        if self.tags is None:
            self.tags = dict()
        self.tags[tag] = value


class SubQuery():
    '''Python variant of AirRecorder SubQuery.
    '''
    def __init__(self, prompt, command, timeout):
        self.prompt = prompt
        self.command = command
        self.timeout = timeout


class Result():
    '''Python variant of AirRecorder Result.
    '''
    def __init__(self, query):
        self.query = query
        self.status = -1
        self.localBeginTime = None
        self.localEndTime = None
        self.remoteBeginTime = None
        self.remoteEndTime = None
        self.remoteRawTime = None
        self.stdout = ""
        self.stderr = ""
        self.throwable = None
        # Optional {tag, value} pairs
        self.resultTags = None

    def setQuery(self, query):
        self.query = query

    def getQuery(self):
        return self.query

    def setStatus(self, status):
        self.status = status

    def getStatus(self):
        return self.status

    def setLocalBeginTime(self, localBeginTime):
        self.localBeginTime = localBeginTime

    def getLocalBeginTime(self):
        return self.localBeginTime

    def setLocalEndTime(self, localEndTime):
        self.localEndTime = localEndTime

    def getLocalEndTime(self):
        return self.localEndTime

    def setRemoteBeginTime(self, remoteBeginTime):
        self.remoteBeginTime = remoteBeginTime

    def getRemoteBeginTime(self):
        return self.remoteBeginTime

    def setRemoteEndTime(self, remoteEndTime):
        self.remoteEndTime = remoteEndTime

    def getRemoteEndTime(self):
        return self.remoteEndTime

    def setRemoteRawTime(self, remoteRawTime):
        self.remoteRawTime = remoteRawTime

    def getRemoteRawTime(self):
        return self.remoteRawTime

    def setStdout(self, stdout):
        self.stdout = stdout

    def getStdout(self):
        return self.stdout

    def setStderr(self, stderr):
        self.stderr = stderr

    def getStderr(self):
        return self.stderr

    def getThrowable(self):
        return self.throwable

    def setResultTags(self, tags):
        self.resultTags = tags

    def getResultTags(self):
        return self.resultTags

    def addResultTag(self, tag, value):
        if self.resultTags is None:
            self.resultTags = dict()
        self.resultTags[tag] = value


'''
#
# Parse an AirRecorder log file and yield on each result

/////
///// Message: RESULT
///// Status: 1319
///// LocalBeginTime: 1311238912292 (2011-07-21T11:01:52.292+0200)
///// LocalEndTime: 1311238912326 (2011-07-21T11:01:52.326+0200)
///// RemoteBeginTime: 1311238824000 (2011-07-21T11:00:24.000+0200)
///// RemoteEndTime: 1311238824034 (2011-07-21T11:00:24.034+0200)
///// Command: show ap debug client-table ap-name 00:24:6c:ce:69:92
///// Section: Stdout
[text]
[///// Section: xxxxx
[text]
.....

#
'''


def _endSection(section, result, lines):
    if (section is not None):
        if (section.startswith('Stdout')):
            result.setStdout(lines)


def parseLogFileGenerator(fileName, tailSleepTime, sleep=time.sleep):
    messageBegin = "///// \n"
    messageEnd = ".....\n"
    result = None
    section = None
    lines = ""
    # AirRecorder header lines are always terminated with \r\n
    # Python3 universal newlines are disabled to ensure that the section content (i.e. Stdout/Stderr)
    # is read in as-is.
    logFile = open(fileName, 'r', newline='\n')
    while True:
        line = logFile.readline()
        if not line:
            # EOF reached
            if tailSleepTime < 0:
                logFile.close()
                return
            if tailSleepTime > 0:
                sleep(tailSleepTime)
            continue

        line_ = line.replace("\r", "")
        if line_ == messageBegin:
            # Message begin
            lines = ""
            query = Query(None)
            result = Result(query)
            continue

        if line_.startswith("///// "):
            # Message header
            _endSection(section, result, lines)
            line = line.rstrip()
            header = line[6:].split(' ')
            tag = header[0]
            if (tag.startswith('Message:')):
                pass
            elif (tag.startswith('Status:')):
                result.setStatus(int(header[1]))
            elif (tag.startswith('LocalBeginTime:')):
                result.setLocalBeginTime(int(header[1]))
            elif (tag.startswith('LocalEndTime:')):
                result.setLocalEndTime(int(header[1]))
            elif (tag.startswith('RemoteBeginTime:')):
                result.setRemoteBeginTime(int(header[1]))
            elif (tag.startswith('RemoteEndTime:')):
                result.setRemoteEndTime(int(header[1]))
            elif (tag.startswith('RemoteRawTime:')):
                # 6(///// ) + 14(RemoteRawTime:) + 1( )
                result.setRemoteRawTime(line[21:])
            elif (tag.startswith('QueryTag:')):
                # 6(///// ) + 9(QueryTag:) + 1( )
                queryTagRaw = line[16:].split('=', 2)
                result.getQuery().addTag(queryTagRaw[0], queryTagRaw[1])
            elif (tag.startswith('ResultTag:')):
                # 6(///// ) + 10(ResultTag:) + 1( )
                resultTagRaw = line[17:].split('=', 2)
                result.addResultTag(resultTagRaw[0], resultTagRaw[1])
            elif (tag.startswith('Command:')):
                # 6(///// ) + 8(Command:) + 1( )
                command = line[15:]
                result.getQuery().setCommand(command)
            elif (tag.startswith('Section:')):
                section = header[1]
            continue

        if line_ == messageEnd:
            # Message ends
            _endSection(section, result, lines)
            yield result
            result = None
            continue

        # Otherwise consume text
        if section is not None:
            lines += line


class LogFileReaderGenerator():
    '''Parse an AirRecorder log file and generate all results
    '''
    def __init__(self, fileName, tailSleepTime=-1):
        self._fileName = fileName
        self._tailSleepTime = tailSleepTime

    def __iter__(self):
        self._g = parseLogFileGenerator(self._fileName, self._tailSleepTime)
        return self

    # Python 3 compatibility
    def __next__(self):
        return next(self._g)


class LogFileProcessor():
    '''Parse an AirRecorder log file and call processResult() for each RESULT
    '''
    def __init__(self, fileName, tailSleepTime=-1):
        self._fileName = fileName
        self._tailSleepTime = tailSleepTime

    def run(self):
        # Generate results
        results = LogFileReaderGenerator(self._fileName, tailSleepTime=self._tailSleepTime)
        for result in results:
            if result.getStatus() <= 0:
                continue
            query = result.getQuery()
            if query is None:
                continue
            command = query.getCommand()
            if command is None:
                continue
            self.processResult(command, result)

    def processResult(self, command, result):
        pass
