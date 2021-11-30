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
# ARCLI parser.
#
# Authors: Thomas Bastian, Jeff Goff
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
import time
from ..CliParserBase import CliParser
from .ArCliResult import ArCliResult
from aacommons.dataparser.cli.TableHelpers import contentAsListOfDict, contentAsParameterValueList


# Default field name separator
ND_FIELD_NAME_SEPARATOR='.'
# Internal, not exposed
TAG_ND_ID='nd.id'


# Logger
log = logging.getLogger(__name__)
logDisp = logging.getLogger(__name__ + "#dispatch")
logAr = logging.getLogger(__name__ + "#parser")


def arCliProcessRecordBeginEnd(record, source):
    # Pre-process source
    r_begin = None
    if 'begin' in record:
        recordBeginCompiledRegex, recordBeginRegex = record['begin']
        m = re.search(recordBeginCompiledRegex, source)
        # If a regex is specified it needs to match
        if m is None:
            logAr.debug("record.begin regex: [%s] did NOT match" % (recordBeginRegex))
            return None
        r_begin = m.start()
    r_end = None
    if 'end' in record:
        recordEndCompiledRegex, recordEndRegex = record['end']
        m = re.search(recordEndCompiledRegex, source)
        # If a regex is specified it needs to match
        if m is None:
            logAr.debug("record.end regex: [%s] did NOT match" % (recordEndRegex))
            return None
        r_end = m.start()
    if r_begin is not None or r_end is not None:
        if r_begin is None:
            # Default to beginning of CLI output
            r_begin = 0
        olen = len(source)
        if r_end is None:
            # Default to end of CLI output
            r_end = olen
        logAr.debug("record text [%d:%d] out of %d" % (r_begin, r_end, olen))
        return source[r_begin:r_end]
    return source


def arCliProcessRecords(records, command, cliOutput, P):
    # Walk through all record directives
    logAr.debug('records: %d, command: %s' % (len(records), command))
    all_records = []
    for record in records:
        logAr.debug("starting process record entry - %s", record)
        r_source = arCliProcessRecordBeginEnd(record, cliOutput)
        if r_source is None:
            logAr.debug("begin or end regex not matching, skipping record entry - %s" % record)
            continue
        r_options = record.get('roptions', {})
        (startCompiledRegex, startRegex, startRegexMode, startRegexOp) = record['start']
        hasStop = 'stop' in record
        if hasStop:
            (stopCompiledRegex, stopRegex, stopRegexMode, stopRegexOp) = record['stop']
        r_command = None
        r_start = None
        r_stop = None
        r_offset = 0
        r_regex_op = 'start'
        r_records = []
        while True:
            # Look for startRegex or stopRegex starting at current offset
            r_text = r_source[r_offset:]
            logAr.debug("record entry %s, regex op %s" % (record, r_regex_op))
            if r_regex_op == 'start':
                m = startRegexOp(startCompiledRegex, r_text)
                if hasStop:
                    # Next regex is 'stop'
                    r_regex_op = 'stop'
                    r_start = r_stop = r_command = None
            else:
                m = stopRegexOp(stopCompiledRegex, r_text)
                # Always fallback to start
                r_regex_op = 'start'
            if m is None:
                # TODO: check for stop case here
                logAr.debug("ending process record entry - %s", record)
                if r_start is not None:
                    # Last record
                    r_records.append((r_command, r_source[r_start:]))
                break
            if r_start is None:
                # Record start
                r_start = r_offset + m.end()
            else:
                # Record stop
                r_stop = r_offset + m.start()
                r_records.append((r_command, r_source[r_start:r_stop]))
                r_start = r_offset + m.end()
            # By default we merge original command with new derived command
            r_prefix = command + ":"
            if not r_options.get('prefix', True):
                r_prefix = ""
            r_command = r_prefix + r_text[m.start():m.end()].rstrip()
            r_offset += m.end()
        logAr.debug("record entry %s produced %d records" % (record, len(r_records)))
        all_records.extend(r_records)
    return all_records


def arCliProcessRegexes(regexes, cliOutput, filterMode, P):
    matched = 0
    for (compiledRegex, regex, regexMode, regexOp) in regexes:
        if regexMode != filterMode:
            continue
        m = regexOp(compiledRegex, cliOutput)
        if not m:
            log.debug("failed regex: [%s]" % regex)
            if logAr.isEnabledFor(logging.DEBUG):
                logAr.debug("failed output: [%s]" % cliOutput)
            continue

        if logAr.isEnabledFor(logging.DEBUG):
            logAr.debug("matched regex: [%s] -> %s" % (regex, m.groupdict()))

        P.update(m.groupdict())
        matched += 1
    return matched


def arCliParseTables(tables, cliOutput, T):
    for table in tables:
        name = table['name']
        kind = table['type']
        marker = table['marker']
        ttext = cliOutput
        tstart = None
        (tbegin_re, tbegin_regex) = table['begin']
        if tbegin_re != None:
            m = re.search(tbegin_re, cliOutput)
            # If a regex is specified it needs to match
            if m is None:
                logAr.debug("table begin regex %s not matching, skipping table" % tbegin_regex)
                continue
            tstart = m.start()
        tend = None
        (tend_re, tend_regex) = table['end']
        if tend_re != None:
            m = re.search(tend_re, cliOutput)
            # If a regex is specified it needs to match
            if m is None:
                logAr.debug("table end regex %s not matching, skipping table" % tend_regex)
                continue
            tend = m.start()
        if tstart is not None or tend is not None:
            if tstart is None:
                # Default to beginning of CLI output
                tstart = 0
            olen = len(cliOutput)
            if tend is None:
                # Default to end of CLI output
                tend = olen
            logAr.debug("table text [%d:%d] out of %d" % (tstart, tend, olen))
            ttext = cliOutput[tstart:tend]
        logAr.debug('parsing table: %s/%s/%s' % (name, kind, marker))
        if kind == 0:
            # Table
            tableOptions=table['toptions']
            ttranspose = False if tableOptions is None else tableOptions.get('nd.transpose', False)
            if ttranspose:
                # Do transposition
                headerList = []
                rows = contentAsListOfDict(ttext, marker=marker, headerList=headerList, tableOptions=tableOptions)
                logAr.debug("parsed table(transposition): %s, rows: %d" % (name, len(rows)))
                if len(rows) > 0 and len(headerList) > 0 and len(headerList[0]) >= 2:
                    # Transposition only makes sense with two or more columns
                    nrows = []
                    for k in headerList[0][1:]:
                        nrow = {}
                        nrow[headerList[0][0]] = k
                        for r in rows:
                            nrow[r[headerList[0][0]]] = r[k]
                        nrows.append(nrow)
                    rows = nrows
                    logAr.debug("parsed table(transposed): %s, rows: %d" % (name, len(rows)))
            else:
                rows = contentAsListOfDict(ttext, marker=marker, tableOptions=tableOptions)
                logAr.debug("parsed table: %s, rows: %d" % (name, len(rows)))
        else:
            # KVP
            _rows = contentAsParameterValueList(ttext, marker=marker)
            rows = [ _rows ]
            logAr.debug("parsed kvp: %s, columns: %d" % (name, len(rows)))
        T.append((table, rows))


def arCliParse(cliCommandDef, cliOutput, P, T, L):
    # Regexes
    regexes = cliCommandDef['regexes']
    if len(regexes) > 0:
        # Entire output against regexes that demand it
        arCliProcessRegexes(regexes, cliOutput, 0, P)

        # Line by line regexes need entire output broken down by lines
        if cliCommandDef['regexes_byline'] > 0:
            logAr.debug("regexes line by line %d" % (cliCommandDef['regexes_byline']))
            # TODO: should this be splitlines() instead?
            lines = cliOutput.split('\n')
            L.extend(lines)

    # Tables
    tables = cliCommandDef['tables']
    if len(tables) > 0:
        arCliParseTables(tables, cliOutput, T)


def _bodyNumberConversion(body, mappings):
    anomalies = { }
    for (k, v) in body.items():
        # Do nothing when v is None
        if v is None:
            anomalies[k] = (v, None)
            continue
        # Special processing for mappings
        if k in mappings:
            if mappings[k] == 'string':
                if type(v) == str:
                    # Already string
                    continue
                else:
                    # Convert to string
                    try:
                        body[k] = str(v)
                        continue
                    except Exception as e:
                        anomalies[k] = (v, e)
                        continue
            # Otherwise fall-through and convert to number

        # Try plain integer/long
        try:
            body[k] = int(v)
            continue
        except:
            # Swallow and fall-through
            pass
        # Try float
        try:
            body[k] = float(v)
            continue
        except ValueError:
            # Leave as is
            pass
        except Exception as e:
            # Report as failed conversion
            anomalies[k] = (v, e)
            continue
    return anomalies


def _arCliProcessField(body, field, ndContext, P=None, C=None):
    fieldName = field['name']
    when = field['when']
    if when != None:
        try:
            if not eval(when):
                logAr.debug('field: skipping %s: when is false' % (fieldName))
                return
        except:
            # When failed, treat as false
            logAr.debug('field: skipping %s: when failed' % (fieldName))
            return

    fieldEName = field['ename']
    if fieldEName != None:
        fieldName = eval(fieldEName)
        logAr.debug('field: ename: %s' % (fieldName))

    if 'P' in field and P != None and field['P'] in P:
        # P assignment
        logAr.debug('P: %s for field: %s' % (field['P'], fieldName))
        body[fieldName] = P[field['P']]
        return

    if 'C' in field and C != None and field['C'] in C:
        # C assignment
        logAr.debug('C: %s for field: %s' % (field['C'], fieldName))
        body[fieldName] = C[field['C']]
        return

    if 'eval' in field:
        # The expression argument is parsed and evaluated as a python expression
        # (technically speaking, a condition list) using the globals and locals
        # dictionaries as global and local namespace. If the globals dictionary
        # is present and lacks '__builtins__', the current globals are copied
        # into globals before expression is parsed. This means that expression
        # normally has full access to the standard __builtin__ module and
        # restricted environments are propagated. If the locals dictionary is
        # omitted it defaults to the globals dictionary. If both dictionaries
        # are omitted, the expression is executed in the environment where eval()
        # is called. The return value is the result of the evaluated expression.
        # eval(expression[, globals[, locals]])
        try:
            result = eval(field['eval'])
        except KeyError as e:
            logAr.warning("KeyError exception [%s] in field [%s], for eval [%s], needs when clause" % \
                (e, field['name'], field['eval']))
            if C is not None:
                logAr.warning("C: [%s]", C)
            if P is not None and len(P) > 0:
                logAr.warning("P: [%s]", P)
            return
        except IndexError as e:
            # protect against dodgy evals
            logAr.warning("IndexError exception [%s] in field [%s], for eval [%s], needs when clause" % \
                (e, field['name'], field['eval']))
            if C is not None:
                logAr.warning("C: [%s]", C)
            if P is not None and len(P) > 0:
                logAr.warning("P: [%s]", P)
            return

        body[fieldName] = result
        return


def _arCliProcessTableRegexes(source, tableDef, name, body, P, C):
    for tableRegex in tableDef['regexes']:
        tableColumn = tableRegex['column']
        if not tableColumn in C:
            continue
        tableWhen = tableRegex['when']
        if tableWhen != None:
            # Only process regex when evaluation returns true
            try:
                if not eval(tableWhen):
                    logAr.debug("[%s] skipping %s: when is false" % \
                                (source, tableColumn))
                    continue
            except:
                # When failed, treat as false
                logAr.debug("[%s] skipping %s: when failed" % \
                            (source, tableColumn))
                continue
        # tableRegex['regex'] is precompiled in NdContext to be a tuple, despite the .json
        # being a single regex string.
        (tableCompiledRe, tableRe, regexOp) = tableRegex['regex']
        m = regexOp(tableCompiledRe, C[tableColumn])
        if not m:
            logAr.debug("[%s] failed table regex: [%s] column:[%s] value:[%s]" % \
                        (source, tableRe, tableColumn, C[tableColumn]))
            continue
        tableDefaults = tableRegex['defaults']
        for (k, v) in m.groupdict().items():
            # handle defaults for certain cases where the groupdict
            # returns None intentionally, i.e. "HT mode" for legacy/non-HT
            if logAr.isEnabledFor(logging.DEBUG):
                logAr.debug("   [%s] [%s] td %s" % (k, v, tableDefaults))
            if v is None:
                newVal = None
                if tableDefaults is not None:
                    newVal = tableDefaults.get(k, None)
                if newVal is not None:
                    logAr.debug("[%s] [%s] [%s] update value [%s][%s] -> [%s]" % \
                               (source, tableColumn, C[tableColumn], k, v, newVal))
                    v = newVal
                else:
                    # No sense to store None value, skip it
                    logAr.debug("[%s] [%s] [%s] update value [%s][%s] -> no default value!" % \
                                (source, tableColumn, C[tableColumn], k, v))
                    continue
            body[name + ND_FIELD_NAME_SEPARATOR + k] = v
        # Needed in case fields reference P
        P.update(m.groupdict())


class ArCliParser(CliParser):
    def __init__(self, parserContext):
        super().__init__()
        self._parserContext = parserContext
        # Label is of the form <device class>/<qualifier>
        # For now we fill only by <device class>
        self._parserMessageHandlerByLabel = dict()
        self._parserMessageHandlerByLabel["ACX"] = ArCliMessageHandlerAcx("ACX/*")
        self._parserMessageHandlerByLabel["AOS"] = ArCliMessageHandlerAos("AOS/*")
        self._parserMessageHandlerByLabel["ASW"] = ArCliMessageHandlerAsw("ASW/*")
        self._parserMessageHandlerByLabel["COMWARE"] = ArCliMessageHandlerComware("COMWARE/*")
        self._parserMessageHandlerByLabel["IAP"] = ArCliMessageHandlerIap("IAP/*")

    def parse(self, parserData):
        # Lookup by full label
        label = parserData['Label']
        parserMessageHandler = self._parserMessageHandlerByLabel.get(label, None)
        if parserMessageHandler is None:
            # Lookup by device class
            dclass = label.split('/')[0]
            parserMessageHandler = self._parserMessageHandlerByLabel.get(dclass, None)
            if parserMessageHandler is None:
                raise Exception(label)
        results = parserMessageHandler.ARRESULT(None, parserData, self._parserContext)
        return results


####
#
# Base message handler, do not put product specific code in this class
#
class ArCliMessageHandler():
    def __init__(self, kind):
        self._byCommandHandler = self.getCommandHandlers()
        self._kind = kind
        self._log = log
        self._log.debug("ArCliMessageHandler inited - %s" % self._kind)

    def ARRESULT(self, topic, jsonData, ndContext):
        try:
            command = jsonData['Command']
            commandHandler = self._byCommandHandler.get(command, self.processArCli)
            if self._log.isEnabledFor(logging.DEBUG):
                self._log.debug("[%s] CLI cmd: [%s] hdl: %s" % \
                    (jsonData.get("Source", "unknown"), command, commandHandler.__name__))
            results = commandHandler(command, jsonData, ndContext)
            return results
        except:
            self._log.critical("Exception in label %s commandHandler %s " % (jsonData['Label'], commandHandler.__name__), exc_info=True)
            self._log.critical('-'*60)
            self._log.critical("-- topic: %s " % topic)
            self._log.critical("-- command: %s " % command)
            self._log.critical("-- JSON: [%s]" % jsonData)

    def dumpCommandHandlers(self):
        self._log.info("%s command handlers" % self._kind)
        for k, v in self._byCommandHandler.items():
            self._log.info("    %-24s  ->  %s" % (k, v.__name__))

    def getCommandHandlers(self):
        return None

    def processArCli(self, command, jsonData, ndContext):
        self._log.debug("[%s] [%s] [%s] - process" % \
            (jsonData['Source'], jsonData['Label'], command))
        if logAr.isEnabledFor(logging.DEBUG):
            logAr.debug(jsonData)

        ndStats = []
        t0 = time.perf_counter()
        P = dict() # Holds parameters by name
        arCliDocuments = ndContext.getArCliDocumentsByLabel(jsonData['Label'])
        if arCliDocuments is None:
            self._log.info("Label %s has no arCliDocuments" % jsonData['Label'])
            return
        cliCommandDef = arCliDocuments.get(command, None)

        if cliCommandDef is None:
            for (compiledRegex, _cliCommandDef) in arCliDocuments['_']:
                m = re.search(compiledRegex, command)
                if m != None:
                    cliCommandDef = _cliCommandDef
                    P.update(m.groupdict())
                    break
            if cliCommandDef is None:
                self._log.info("[%s] [%s] [%s] drop - no cliCommandDef" % \
                    (jsonData['Source'], jsonData['Label'], command))
                return

        # Records
        records = cliCommandDef['records']
        if len(records) > 0:
            # Preprocess CLI output for records
            precords = arCliProcessRecords(records, command, jsonData['Stdout'], P)
            self._log.info("extracted %d records from [%s]" % (len(precords), command))
            if logAr.isEnabledFor(logging.DEBUG):
                logAr.debug(precords)
            results = []
            for precord in precords:
                (r_command, r_stdout) = precord
                r_jsonData = jsonData.clone()
                r_jsonData['Stdout'] = r_stdout
                r_jsonData['Command'] = r_command
                r_jsonData['Status'] = len(r_stdout)
                # TODO: drop topic
                r_results = self.ARRESULT(None, r_jsonData, ndContext)
                if r_results is not None:
                    if isinstance(r_results, tuple):
                        results.append(r_results)
                    elif isinstance(r_results, list):
                        results.append((r_command, r_results))
                    else:
                        raise Exception("not a tuple or list")
                else:
                    results.append((r_command, None))
            return (command, results)

        source = jsonData['Source']
        localTime = jsonData['LocalBeginTime']
        stdout = jsonData['Stdout']
        outputTags = jsonData.getOutputTags(ndContext, source)
        bodyTags = jsonData.getBodyTags(ndContext, source)
        t1 = time.perf_counter()
        ndStats.append(('time', source, 'arcli.dispatch_ms', (t1 - t0) * 1000.0))

        result = None
        try:
            result = self.arCliHandler(cliCommandDef, ndContext, source, bodyTags, outputTags, localTime, stdout, P, ndStats, jsonData)
        except Exception as e:
            self._log.error("Exception in arCliHandler: %s" % e, exc_info=True)

        # Post ND statistics
        # TODO: rework
        if False and ndContext.isSystemFullStats():
            # Each entry has tuple (event_type, event_source, event_group, event_increment)
            for (event_type, event_source, event_group, event_increment) in ndStats:
                ndContext.addSystemFullStats(event_type, event_source, event_group, event_increment)
        return (command, result)

    def arCliHandler(self, cliCommandDef, ndContext, source, bodyTags, outputTags, timeStamp, cliOutput, P, ndStats, jsonData):
        t0 = time.perf_counter()
        # Add system and platform tags as parameters
        P['source'] = source
        P.update(bodyTags)
        # Holds tables
        T = []
        # Holds line by line
        L = []
        # Parse content
        t1 = time.perf_counter()
        arCliParse(cliCommandDef, cliOutput, P, T, L)
        t2 = time.perf_counter()

        if logAr.isEnabledFor(logging.DEBUG):
            logAr.debug('P: %s' % P)
            logAr.debug('len(P): %d' % len(P))
            logAr.debug('len(T): %d' % len(T))
            logAr.debug('len(L): %d' % len(L))

        t3 = time.perf_counter()
        ndStats.append(('time', source, 'arcli.prepare_ms', (t1 - t0) * 1000.0))
        ndStats.append(('time', source, 'arcli.parse_ms', (t2 - t1) * 1000.0))

        if not jsonData.processDocument(ndContext, source, cliCommandDef):
            self._log.debug("processDocument returned False, skip processing document")
            return None
        result = self.arCliProcessDocument(cliCommandDef, ndContext, source, bodyTags, outputTags, timeStamp,
                                           P, T, L, ndStats, jsonData)
        t3 = time.perf_counter()
        ndStats.append(('time', source, 'arcli.process_ms', (t3 - t2) * 1000.0))
        return result

    def arCliProcessDocument(self, cliCommandDef, ndContext, source, bodyTags, outputTags, timeStamp,
                             P, T, L, ndStats, jsonData):
        t0 = time.perf_counter()
        fields = cliCommandDef['fields']
        doc_type = cliCommandDef['document']
        result = ArCliResult()
        # Process regex
        result.addType(ArCliResult.TYPE_REGEXES_ENTIRE)
        if cliCommandDef['regexes_entire'] > 0:
            body = {}
            for field in fields:
                fieldName = field['name']
                # TODO: revisit filtering
                if False and not field['enabled']:
                    logAr.debug('field: skipping %s: not enabled' % (fieldName))
                    continue
                _arCliProcessField(body, field, ndContext, P)
            # Single document
            messages = result.addSection(ArCliResult.TYPE_REGEXES_ENTIRE)
            self.arCliMessagePost(ndContext, source, bodyTags, outputTags, timeStamp, doc_type, body, messages, jsonData)
        # regex process done
        t1 = time.perf_counter()
        # Process tables
        result.addType(ArCliResult.TYPE_TABLES)
        if len(T) > 0:
            savedP = P
            for (tableDef, rows) in T:
                name = tableDef['name']
                logAr.debug('processing tables rows: %s' % (name))
                messages = result.addSection(ArCliResult.TYPE_TABLES, name)
                for C in rows:
                    body = {}
                    P = dict()
                    P.update(savedP)
                    # Add row content as fields
                    for (k, v) in C.items():
                        body[name + ND_FIELD_NAME_SEPARATOR + k] = v
                    # Process table regexes
                    _arCliProcessTableRegexes(source, tableDef, name, body, P, C)
                    # Process fields
                    for field in fields:
                        fieldName = field['name']
                        # TODO: revisit filtering
                        if False and not field['enabled']:
                            logAr.debug('field: skipping %s: not enabled' % (fieldName))
                            continue
                        _arCliProcessField(body, field, ndContext, P, C)
                    # Single document per table row
                    # TODO: add a document override for the table and field
                    tableTimestamp = tableDef['timestamp']
                    if tableTimestamp != None:
                        # Evaluation returns floating point time, convert to ms
                        evalTableTimestamp = eval(tableTimestamp)
                        timeStampMillis = evalTableTimestamp * 1000.0
                        # Need to force a static id otherwise
                        idkey = eval(tableDef['idkey'])
                        body[TAG_ND_ID] = name + ("%f" % timeStampMillis) + idkey
                        self.arCliMessagePost(ndContext, source, bodyTags, outputTags, evalTableTimestamp, doc_type, body, messages, jsonData)
                    else:
                        self.arCliMessagePost(ndContext, source, bodyTags, outputTags, timeStamp, doc_type, body, messages, jsonData)
            P = savedP
        # T processing done
        t2 = time.perf_counter()
        # Process line by line regex
        result.addType(ArCliResult.TYPE_REGEXES_BYLINE)
        if len(L) > 0:
            regexes = cliCommandDef['regexes']
            logAr.debug('processing line by line regexes: %s' % (regexes))
            savedP = P
            for row in L:
                P = dict()
                arCliProcessRegexes(regexes, row, 1, P)
                if len(P) > 0:
                    messages = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
                    body = {}
                    P.update(savedP)
                    for field in fields:
                        fieldName = field['name']
                        # TODO: revisit filtering
                        if False and not field['enabled']:
                            logAr.debug('field: skipping %s: not enabled' % (fieldName))
                            continue
                        _arCliProcessField(body, field, ndContext, P)
                    # Single document per line
                    self.arCliMessagePost(ndContext, source, bodyTags, outputTags, timeStamp, doc_type, body, messages, jsonData)
        # line by line done
        t3 = time.perf_counter()
        ndStats.append(('time', source, 'arcli.procdoc.proc_regex_ms', (t1 - t0) * 1000.0))
        ndStats.append(('time', source, 'arcli.procdoc.proc_T_ms', (t2 - t1) * 1000.0))
        ndStats.append(('time', source, 'arcli.procdoc.proc_L_ms', (t3 - t2) * 1000.0))
        return result.get()

    def arCliMessagePost(self, ndContext, source, bodyTags, outputTags, timeStamp, doc_type, body, messages, jsonData):
        if len(body) == 0:
            # No data was copied
            return
        # Add body tags
        body.update(bodyTags)
        # Body conversion
        anomalies = _bodyNumberConversion(body, ndContext.getArCliMappings())
        if len(anomalies) > 0:
            # Report conversion anomalies
            log.warning('number conversion: [%s] %s %s anomalies: %s' % (source, doc_type, body, anomalies))
        # Final object
        output = {}
        output['timestamp'] = float(timeStamp)
        if outputTags is not None:
            output.update(outputTags)
        output['body'] = body
        _id = body.get(TAG_ND_ID, None)
        if _id != None:
            del body[TAG_ND_ID]
            output[TAG_ND_ID] = _id
        outputMessages = jsonData.updateMessageTags(ndContext, source, doc_type, output)
        if outputMessages is not None:
            if self._log.isEnabledFor(logging.DEBUG):
                for (d, o) in outputMessages:
                    self._log.debug('[%s] %s %s' % (source, d, o))
            messages.extend(outputMessages)


########################################
#
# Per Product ARCLI Handlers Start Here
# As these grow longer they should probably move to their
# own files to avoid clutter
#

#
# ArubaOS-CX Switch
#
class ArCliMessageHandlerAcx(ArCliMessageHandler):
    def __init__(self, kind):
        super().__init__(kind)
        self._byCommandHandler = self.getCommandHandlers()
        self._log = logging.getLogger(__name__ + "#handler#acx")
        self.dumpCommandHandlers()

    def getCommandHandlers(self):
        byCommandHandler = dict()
        return byCommandHandler


#
# ArubaOS-Switch (Procurve)
#
class ArCliMessageHandlerAsw(ArCliMessageHandler):
    def __init__(self, kind):
        super().__init__(kind)
        self._byCommandHandler = self.getCommandHandlers()
        self._log = logging.getLogger(__name__ + "#handler#asw")
        self.dumpCommandHandlers()

    def getCommandHandlers(self):
        byCommandHandler = dict()
        return byCommandHandler


#
# Aruba IAP
#
class ArCliMessageHandlerIap(ArCliMessageHandler):
    def __init__(self, kind):
        super().__init__(kind)
        self._byCommandHandler = self.getCommandHandlers()
        self._log = logging.getLogger(__name__ + "#handler#iap")
        self.dumpCommandHandlers()

    def getCommandHandlers(self):
        byCommandHandler = dict()
        return byCommandHandler


#
# Comware Switch
#
class ArCliMessageHandlerComware(ArCliMessageHandler):
    def __init__(self, kind):
        super().__init__(kind)
        self._byCommandHandler = self.getCommandHandlers()
        self._log = logging.getLogger(__name__ + "#handler#comware")
        self.dumpCommandHandlers()

    def getCommandHandlers(self):
        byCommandHandler = dict()
        byCommandHandler['display cpu'] = self.processDisplayCpu
        byCommandHandler['display mpls ldp peer verbose'] = self.processDisplayMplsLdpPeerVerbose
        byCommandHandler['display ospf statistics packet'] = self.processDisplayOspfStatisticsPacket
        return byCommandHandler

    def processDisplayCpu(self, command, jsonData, ndContext):
        self._log.debug("process for source %s" % jsonData['Source'])
        source = jsonData['Source']
        localTime = jsonData['LocalBeginTime']
        outputTags = jsonData.getOutputTags(ndContext, source)
        bodyTags = jsonData.getBodyTags(ndContext, source)
        stdout = jsonData['Stdout'].replace('\r', '')
        # Expect definition to be present in arcli.json
        arCliDocuments = ndContext.getArCliDocumentsByLabel(jsonData['Label'])
        if arCliDocuments is None:
            return
        result = ArCliResult()
        result.addType(ArCliResult.TYPE_REGEXES_BYLINE)
        messages = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
        cliCommandDef = arCliDocuments.get(command, None)
        regexes = cliCommandDef['regexes']
        lines = stdout.splitlines()
        ln = 0
        while ln < len(lines):
            line = lines[ln].strip()
            if line == "":
                ln += 1
                continue
            P = dict()
            if arCliProcessRegexes(regexes, line, 0, P):
                # Slot \d+ CPU \d+ CPU usage:
                if (ln + 3) < len(lines):
                    # Read in values
                    cpu5second = int(lines[ln + 1].strip().split('%')[0])
                    cpu1minute = int(lines[ln + 2].strip().split('%')[0])
                    cpu5minutes = int(lines[ln + 3].strip().split('%')[0])
                    doc_type = "COMWARE_CPU"
                    body = {
                        'comware.cpu.slot': P['slot'],
                        'comware.cpu.id': P['cpu'],
                        'comware.cpu.util5second': cpu5second,
                        'comware.cpu.util1minute': cpu1minute,
                        'comware.cpu.util5minutes': cpu5minutes
                    }
                    self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, doc_type, body, messages, jsonData)
                    ln += 3
                    continue
            ln += 1
        return (command, result.get())

    def processDisplayMplsLdpPeerVerbose(self, command, jsonData, ndContext):
        self._log.debug("process for source %s" % jsonData['Source'])
        source = jsonData['Source']
        localTime = jsonData['LocalBeginTime']
        outputTags = jsonData.getOutputTags(ndContext, source)
        bodyTags = jsonData.getBodyTags(ndContext, source)
        result = ArCliResult()
        result.addType(ArCliResult.TYPE_REGEXES_BYLINE)
        messages = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
        stdout = jsonData['Stdout'].replace('\r', '')
        lines = stdout.splitlines()
        prefix = "comware.mpls.ldp.peer.verbose."
        processingPeer = None
        patternSessionUptime = re.compile("(\\d+)\\:(\\d+)\\:(\\d+) .*")
        patternMsgs = re.compile("(\\d+)\\/(\\d+)")
        patternKA = re.compile("(\\d+)\\/(\\d+)")
        ln = 0
        while ln < len(lines):
            line = lines[ln].strip()
            if line == "":
                if processingPeer is not None:
                    self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, "COMWARE_MPLS_LDP_PEER_VERBOSE", processingPeer, messages, jsonData)
                processingPeer = None
                ln += 1
                continue
            if line.startswith("Peer LDP ID      :"):
                # Detected new peer
                processingPeer = dict()
                processingPeer[prefix + "PeerId"] = line.split(':', 1)[1].strip()
                ln += 1
                continue
            if processingPeer is not None:
                if line.startswith("Session State"):
                    _sessionState = line.split(':', 1)[1].strip().split(' ', 1)[0].strip()
                    processingPeer[prefix + "sessionState"] = _sessionState
                if line.startswith("Session Up Time"):
                    _sessionUptime = line.split(':', 1)[1].strip()
                    splits = re.match(patternSessionUptime, _sessionUptime)
                    processingPeer[prefix + "sessionUptime"] = _sessionUptime
                    processingPeer[prefix + "sessionUptime_"] = int(splits.group(1)) * 86400 + \
                        int(splits.group(2)) * 3600 + int(splits.group(3)) * 60
                if line.startswith("Msgs Sent/Rcvd"):
                    splits = re.match(patternMsgs, line.split(':', 1)[1].strip())
                    processingPeer[prefix + "MsgsSent"] = int(splits.group(1))
                    processingPeer[prefix + "MsgsRcvd"] = int(splits.group(2))
                if line.startswith("KA Sent/Rcvd"):
                    splits = re.match(patternKA, line.split(':', 1)[1].strip())
                    processingPeer[prefix + "KASent"] = int(splits.group(1))
                    processingPeer[prefix + "KARcvd"] = int(splits.group(2))
            ln += 1
        if processingPeer is not None:
            self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, "COMWARE_MPLS_LDP_PEER_VERBOSE", processingPeer, messages, jsonData)
        return (command, result.get())

    def processDisplayOspfStatisticsPacket(self, command, jsonData, ndContext):
        self._log.debug("process for source %s" % jsonData['Source'])
        source = jsonData['Source']
        localTime = jsonData['LocalBeginTime']
        outputTags = jsonData.getOutputTags(ndContext, source)
        bodyTags = jsonData.getBodyTags(ndContext, source)
        result = ArCliResult()
        result.addType(ArCliResult.TYPE_REGEXES_BYLINE)
        messagesGlobal = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
        messagesInterface = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
        stdout = jsonData['Stdout'].replace('\r', '')
        lines = stdout.splitlines()
        prefixGlobal = "comware.ospf.stats.packet.global."
        processingGlobal = None
        patternGlobalIO = re.compile("(\\d+) +(\\d+) +(\\d+) +(\\d+) +(\\d+) +(\\d+)")
        processingArea = None
        prefixInterface = "comware.ospf.stats.packet.interface."
        processingInterface = None
        patternInterfaceIO = re.compile("(\\d+) +(\\d+) +(\\d+) +(\\d+) +(\\d+)")
        ln = 0
        while ln < len(lines):
            line = lines[ln].strip()
            if line.startswith("Waiting to send packet count: "):
                # Detected global stats
                processingGlobal = dict()
                processingGlobal[prefixGlobal + "waiting"] = int(line.split(':', 1)[1].strip())
                ln += 1
                continue
            if processingGlobal is not None:
                if line.startswith("Input : "):
                    _globalInput = line.split(':', 1)[1].strip()
                    splits = re.match(patternGlobalIO, _globalInput)
                    processingGlobal[prefixGlobal + "input.Hello"] = int(splits.group(1))
                    processingGlobal[prefixGlobal + "input.DD"] = int(splits.group(2))
                    processingGlobal[prefixGlobal + "input.LSR"] = int(splits.group(3))
                    processingGlobal[prefixGlobal + "input.LSU"] = int(splits.group(4))
                    processingGlobal[prefixGlobal + "input.ACK"] = int(splits.group(5))
                    processingGlobal[prefixGlobal + "input.Total"] = int(splits.group(6))
                if line.startswith("Output: "):
                    _globalOutput = line.split(':', 1)[1].strip()
                    splits = re.match(patternGlobalIO, _globalOutput)
                    processingGlobal[prefixGlobal + "output.Hello"] = int(splits.group(1))
                    processingGlobal[prefixGlobal + "output.DD"] = int(splits.group(2))
                    processingGlobal[prefixGlobal + "output.LSR"] = int(splits.group(3))
                    processingGlobal[prefixGlobal + "output.LSU"] = int(splits.group(4))
                    processingGlobal[prefixGlobal + "output.ACK"] = int(splits.group(5))
                    processingGlobal[prefixGlobal + "output.Total"] = int(splits.group(6))
            if line.startswith("Area: "):
                # Detected per Area stats
                if processingGlobal is not None:
                    # Publish previous
                    self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, "COMWARE_OSPF_STATISTICS_PACKET_GLOBAL", processingGlobal, messagesGlobal, jsonData)
                    processingGlobal = None
                processingArea = line.split(':', 1)[1].strip()
                ln += 1
                continue
            if line.startswith("Interface: "):
                if processingInterface is not None:
                    # Publish previous
                    self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, "COMWARE_OSPF_STATISTICS_PACKET_INTERFACE", processingInterface, messagesInterface, jsonData)
                processingInterface = dict()
                processingInterface[prefixInterface + "area"] = processingArea
                processingInterface[prefixInterface + "interface"] = line.split(':', 1)[1].strip()
            if processingInterface is not None:
                if line.startswith("Input : "):
                    _interfaceInput = line.split(':', 1)[1].strip()
                    splits = re.match(patternInterfaceIO, _interfaceInput)
                    processingInterface[prefixInterface + "input.DD"] = int(splits.group(1))
                    processingInterface[prefixInterface + "input.LSR"] = int(splits.group(2))
                    processingInterface[prefixInterface + "input.LSU"] = int(splits.group(3))
                    processingInterface[prefixInterface + "input.ACK"] = int(splits.group(4))
                    processingInterface[prefixInterface + "input.Total"] = int(splits.group(5))
                if line.startswith("Output: "):
                    _interfaceOutput = line.split(':', 1)[1].strip()
                    splits = re.match(patternInterfaceIO, _interfaceOutput)
                    processingInterface[prefixInterface + "output.DD"] = int(splits.group(1))
                    processingInterface[prefixInterface + "output.LSR"] = int(splits.group(2))
                    processingInterface[prefixInterface + "output.LSU"] = int(splits.group(3))
                    processingInterface[prefixInterface + "output.ACK"] = int(splits.group(4))
                    processingInterface[prefixInterface + "output.Total"] = int(splits.group(5))
            ln += 1
        if processingInterface is not None:
            self.arCliMessagePost(ndContext, source, bodyTags, outputTags, localTime, "COMWARE_OSPF_STATISTICS_PACKET_INTERFACE", processingInterface, messagesInterface, jsonData)
        return (command, result.get())


#
# ArubaOS Controller
#
class ArCliMessageHandlerAos(ArCliMessageHandler):
    def __init__(self, kind):
        super().__init__(kind)
        self._byCommandHandler = self.getCommandHandlers()
        self._log = logging.getLogger(__name__ + "#handler#aos")
        self._log.debug("ArCliMessageHandlerAos inited")
        self.dumpCommandHandlers()

    def getCommandHandlers(self):
        byCommandHandler = dict()
        byCommandHandler['show datapath message-queue counters'] = self.processShowDatapathMessageQueueCounters
        return byCommandHandler

    def processShowDatapathMessageQueueCounters(self, command, jsonData, ndContext):
        self._log.debug("process for source %s" % jsonData['Source'])
        source = jsonData['Source']
        timeStamp = jsonData['LocalBeginTime']
        outputTags = jsonData.getOutputTags(ndContext, source)
        bodyTags = jsonData.getBodyTags(ndContext, source)
        result = ArCliResult()
        result.addType(ArCliResult.TYPE_REGEXES_BYLINE)
        content = jsonData['Stdout']
        sosmq_start = content.find("Datapath SOS Message Queue Statistics")
        dpimq_start = content.find("Datapath DPI Message Queue Statistics")
        if sosmq_start >= 0:
            # Process SOS section
            messagesSOS = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
            if dpimq_start >= 0:
                content_sos = content[sosmq_start:dpimq_start]
            else:
                content_sos = content[sosmq_start:]
            self.processShowDatapathMessageQueueCountersSos(ndContext, source, bodyTags, outputTags, timeStamp, content_sos, messagesSOS, jsonData)
        if dpimq_start >= 0:
            # Process DPI section
            messagesDPI = result.addSection(ArCliResult.TYPE_REGEXES_BYLINE)
            content_dpi = content[dpimq_start:]
            self.processShowDatapathMessageQueueCountersDpi(ndContext, source, bodyTags, outputTags, timeStamp, content_dpi, messagesDPI, jsonData)
        return (command, result.get())

    def processShowDatapathMessageQueueCountersSos(self, ndContext, source, bodyTags, outputTags, timeStamp, content, messages, jsonData):
        cpus = None
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("Cpu-->"):
                cpus = line.replace("Cpu-->", "").split()
                continue
            if line.startswith("Opcode"):
                continue
            if line.startswith("---"):
                continue
            if line.startswith("Datapath"):
                continue
            if line == "":
                cpus = None
                continue
            if cpus is None:
                continue
            step = 9
            opcode = line[0:step].strip()
            i = step
            for cpu in cpus:
                _hprio = line[i:i+step]
                if _hprio.strip() == "":
                    hprio = None
                else:
                    hprio = int(_hprio, 16)
                _lprio = line[i+step:i+2*step]
                if _lprio.strip() == "":
                    lprio = None
                else:
                    lprio = int(_lprio, 16)
                i += 2 * step
                if hprio is None and lprio is None:
                    continue
                body = {}
                body['aos.dp.message-queue.counters.sos.cpu'] = str(cpu)
                body['aos.dp.message-queue.counters.sos.opcode'] = str(opcode)
                if hprio is not None:
                    body['aos.dp.message-queue.counters.sos.highprio'] = hprio
                if lprio is not None:
                    body['aos.dp.message-queue.counters.sos.lowprio'] = lprio
                self.arCliMessagePost(ndContext, source, bodyTags, outputTags, timeStamp, "AOS_DP_MESSAGE-QUEUE_COUNTERS_SOS", body, messages, jsonData)

    def processShowDatapathMessageQueueCountersDpi(self, ndContext, source, bodyTags, outputTags, timeStamp, content, messages, jsonData):
        cpus = None
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("Cpu->Opcode"):
                cpus = line.replace("Cpu->Opcode", "").split()
                continue
            if line.startswith("---"):
                continue
            if line.startswith("Datapath"):
                continue
            if line == "":
                cpus = None
                continue
            if cpus is None:
                continue
            step = 9
            opcode = line[0:15].strip()
            i = 20
            for cpu in cpus:
                _value = line[i:i+step]
                if _value.strip() == "":
                    value = None
                else:
                    value = int(_value, 16)
                i += step
                if value is None:
                    continue
                body = {}
                body['aos.dp.message-queue.counters.dpi.cpu'] = str(cpu)
                body['aos.dp.message-queue.counters.dpi.opcode'] = str(opcode)
                body['aos.dp.message-queue.counters.dpi.value'] = value
                self.arCliMessagePost(ndContext, source, bodyTags, outputTags, timeStamp, "AOS_DP_MESSAGE-QUEUE_COUNTERS_DPI", body, messages, jsonData)
