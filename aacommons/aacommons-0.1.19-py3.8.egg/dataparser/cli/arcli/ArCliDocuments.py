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
# ARCLI documents.
#
# Authors: Thomas Bastian, Albert Pang
#
'''

'''
# Parameters
'''
'''
#
'''

import jstyleson
import logging
import re
from json import loads


# Logger
log = logging.getLogger(__name__)


class ArCliDocuments():
    def __init__(self, contentProvider, fieldNameSeparator):
        self.load(contentProvider, fieldNameSeparator)

    def load(self, contentProvider, fieldNameSeparator):
        log.info('loading: %s' % (contentProvider))
        arCliContent = contentProvider.getContent()
        arCliDefs = jstyleson.loads(arCliContent)
        arCliSystemMappings = arCliDefs['arcliSystemMappings']
        self.arCliMappings = arCliSystemMappings
        arCliDocumentsByLabel = dict()
        allDocumentDefs = arCliDefs['arcliDocuments']
        for k in allDocumentDefs.keys():
            label = allDocumentDefs[k]['label']
            isDefault = allDocumentDefs[k].get('default', False)
            extendLabel = allDocumentDefs[k].get('extend', None)
            log.info('loading: %s, label: %s, default: %s, extend: %s' %
                     (k, label, isDefault, extendLabel))
            if extendLabel is not None:
                # Find corresponding document key
                _extendK = None
                for extendK in allDocumentDefs.keys():
                    if allDocumentDefs[extendK]['label'] == extendLabel:
                        _extendK = extendK
                if _extendK is None:
                    raise Exception("extend label %s referenced by %s not found" % (extendLabel, k))
                # Merge documents, key "_" needs special treatment
                labeledDocumentDefs = self.load_(arCliDefs[_extendK], fieldNameSeparator)
                labeledDocumentDefsExtend = self.load_(arCliDefs[k], fieldNameSeparator)
                labeledDocumentDefsExtend_ = labeledDocumentDefsExtend.pop("_")
                labeledDocumentDefs.update(labeledDocumentDefsExtend)
                for (k, v) in labeledDocumentDefsExtend_:
                    i = 0
                    while i < len(labeledDocumentDefs["_"]):
                        (k1, _) = labeledDocumentDefs["_"][i]
                        if k == k1:
                            # Replace same key
                            labeledDocumentDefs["_"][i] = (k, v)
                            i = -1
                            break
                        i += 1
                    if i >= 0:
                        # Not found, append key
                        labeledDocumentDefs["_"].append((k, v))
            else:
                labeledDocumentDefs = self.load_(arCliDefs[k], fieldNameSeparator)
            arCliDocumentsByLabel[label] = labeledDocumentDefs
            if isDefault:
                arCliDocumentsByLabel['default/default'] = labeledDocumentDefs
        self.arCliDocumentsByLabel = arCliDocumentsByLabel

    def load_(self, arCliDocumentDefs, fieldNameSeparator):
        arCliDocuments = dict()
        arCliDocuments['_'] = []
        for (cliCommand, loadedCliCommandDef) in arCliDocumentDefs.items():
            log.debug('CLI command: %s' % cliCommand)
            cliCommandDef = dict()

            cliCommandDef['document'] = loadedCliCommandDef['document']
            log.debug('document: %s', cliCommandDef['document'])

            cliCommandParameters = loadedCliCommandDef.get('parameters', False)

            cliCommandGroup = 'none'
            cliCommandGroup = loadedCliCommandDef.get('group', cliCommandGroup)
            log.debug('default group: %s', cliCommandGroup)
            cliCommandDef['group'] = cliCommandGroup

            loadedCommandRecords = loadedCliCommandDef.get('records', None)
            log.debug('loaded records: %s', loadedCommandRecords)
            cliCommandRecords = []
            cliCommandDef['records'] = cliCommandRecords
            if loadedCommandRecords != None:
                for recordDef in loadedCommandRecords:
                    record = dict()
                    # begin and end (optional, default: None)
                    recordBegin = recordDef.get('begin', None)
                    if recordBegin is not None:
                        record['begin'] = (re.compile(recordBegin, flags=re.MULTILINE), recordBegin)
                    recordEnd = recordDef.get('end', None)
                    if recordEnd is not None:
                        record['end'] = (re.compile(recordEnd, flags=re.MULTILINE), recordEnd)
                    # start mandatory
                    record['start'] = parseArCliRegex(cliCommandDef, recordDef['start'])
                    # stop optional
                    if 'stop' in recordDef:
                        record['stop'] = parseArCliRegex(cliCommandDef, recordDef['stop'])
                    # roptions optional
                    recordOptions = recordDef.get('roptions', None)
                    if recordOptions is not None:
                        record['roptions'] = recordOptions
                    cliCommandRecords.append(record)
            log.debug('loaded %d records', len(cliCommandDef['records']))

            loadedCommandRegexes = loadedCliCommandDef.get('regexes', None)
            log.debug('loaded regexes: %s', loadedCommandRegexes)
            cliCommandRegexes = []
            cliCommandDef['regexes'] = cliCommandRegexes
            cliCommandDef['regexes_byline'] = 0
            if loadedCommandRegexes != None:
                for regexDef in loadedCommandRegexes:
                    cliCommandRegex = parseArCliRegex(cliCommandDef, regexDef)
                    cliCommandRegexes.append(cliCommandRegex)
            log.debug('loaded %d regexes (by line)', cliCommandDef['regexes_byline'])
            cliCommandDef['regexes_entire'] = \
                len(cliCommandRegexes) - cliCommandDef['regexes_byline']
            log.debug('loaded %d regexes (entire)', cliCommandDef['regexes_entire'])

            loadedCommandTables = loadedCliCommandDef.get('tables', None)
            log.debug('loaded tables: %s', loadedCommandTables)
            cliCommandTables = []
            cliCommandDef['tables'] = cliCommandTables
            if loadedCommandTables != None:
                for tableDef in loadedCommandTables:
                    cliCommandTable = parseArCliTable(cliCommandDef, tableDef,
                                                      fieldNameSeparator, self.arCliMappings)
                    cliCommandTables.append(cliCommandTable)

            loadedCommandFields = loadedCliCommandDef.get('fields', None)
            log.debug('loaded fields: %s', loadedCommandFields)
            cliCommandFields = []
            cliCommandDef['fields'] = cliCommandFields
            if loadedCommandFields != None:
                for fieldDef in loadedCommandFields:
                    log.debug('processing field: %s', fieldDef)
                    cliCommandField = parseArCliField(cliCommandDef, fieldDef,
                                                      self.arCliMappings)
                    cliCommandFields.append(cliCommandField)

            if cliCommandParameters:
                # Need regex
                log.debug("add regex command: %s" % (cliCommand))
                arCliDocuments['_'].append((re.compile(cliCommand), cliCommandDef))
            else:
                arCliDocuments[cliCommand] = cliCommandDef
        log.info('done')
        return arCliDocuments

    def getByLabel(self, label):
        if self.arCliDocumentsByLabel is None:
            log.debug("no documents available")
            return None
        arCliDocuments = self.arCliDocumentsByLabel.get(label, None)
        if arCliDocuments is None:
            log.debug("no documents for label [%s]" % label)
        return arCliDocuments

    def getMappings(self):
        return self.arCliMappings


def parseArCliRegex(cliCommandDef, regexDef):
    # mode (optional, default: single)
    regexMode = 0
    _regexMode = regexDef.get('mode', None)
    if _regexMode != None:
        if _regexMode == 'line':
            regexMode = 1
            cliCommandDef['regexes_byline'] += 1

    # re.match (optional, default: false)
    regexOp = re.search
    if regexDef.get('re.match', False):
        regexOp = re.match

    # regex
    regex = regexDef['regex']
    log.debug('adding: regex: %s, mode: %d, op: %s' % (regex, regexMode, regexOp))

    try:
        return (re.compile(regex), regex, regexMode, regexOp)
    except re.error as e:
        log.critical("Fatal: re compile failure: %s" % e)
        log.critical("cliCommandDef: %s" % cliCommandDef)
        log.critical("regex: %s, mode: %d, op: %s" % (regex, regexMode, regexOp))
        raise


def parseArCliTable(cliCommandDef, tableDef, fieldNameSeparator, mappings=None):
    cliCommandTable = dict()

    # Table name
    tableName = tableDef['name']
    cliCommandTable['name'] = tableName

    # marker (optional, default: None)
    cliCommandTable['marker'] = tableDef.get('marker', None)
    log.debug('table: %s marker: %s' % (tableName, cliCommandTable['marker']))

    # type (optional, default: table)
    cliCommandTable['type'] = 0
    tableKind = tableDef.get('type', None)
    if tableKind != None:
        if tableKind == 'kvp':
            cliCommandTable['type'] = 1
    log.debug('table: %s type: %s' % (tableName, cliCommandTable['type']))

    # mappings (optional, default: None)
    tableMappings = tableDef.get('mappings', None)
    if tableMappings != None:
        for (k, v) in tableMappings.items():
            # Table fields are of the form: <name>_<column>
            _updateMapping(mappings, cliCommandDef['document'], tableName + fieldNameSeparator + k, v)
    log.debug('table: %s mappings: %s' % (tableName, tableMappings))

    # timestamp (optional, default: None)
    cliCommandTable['timestamp'] = None
    cliCommandTable['idkey'] = None
    tableTimestamp = tableDef.get('timestamp', None)
    if tableTimestamp != None:
        cliCommandTable['timestamp'] = compile(tableTimestamp, tableTimestamp, 'eval')
        idkey = tableDef['idkey']
        cliCommandTable['idkey'] = compile(idkey, idkey, 'eval')
        log.debug('table: %s timestamp: %s idkey: %s' % (tableName, cliCommandTable['timestamp'],
                                                         cliCommandTable['idkey']))

    # regexes (optional, default: None)
    cliCommandTable['regexes'] = []
    tableRegexes = tableDef.get('regexes', None)
    if tableRegexes != None:
        for tableRegex in tableRegexes:
            cliCommandTableRegex = dict()
            cliCommandTableRegex['column'] = tableRegex['column']
            regexOp = re.search
            if tableRegex.get('re.match', False):
                regexOp = re.match
            cliCommandTableRegex['regex'] = \
                (re.compile(tableRegex['regex']), tableRegex['regex'], regexOp)
            regexMappings = tableRegex.get('mappings', None)
            if regexMappings != None:
                for (k, v) in regexMappings.items():
                    # Table fields are of the form: <name>_<column>
                    _updateMapping(mappings, cliCommandDef['document'], tableName + fieldNameSeparator + k, v)
            cliCommandTable['regexes'].append(cliCommandTableRegex)
            cliCommandTableRegex['when'] = tableRegex.get('when', None)
            cliCommandTableRegex['defaults'] = tableRegex.get('defaults', None)

    # begin and end (optional, default: None)
    cliCommandTable['begin'] = (None, None)
    tableBegin = tableDef.get('begin', None)
    if tableBegin != None:
        cliCommandTable['begin'] = (re.compile(tableBegin, flags=re.MULTILINE), tableBegin)
    cliCommandTable['end'] = (None, None)
    tableEnd = tableDef.get('end', None)
    if tableEnd != None:
        cliCommandTable['end'] = (re.compile(tableEnd, flags=re.MULTILINE), tableEnd)

    # table options (optional, default: None)
    cliCommandTable['toptions'] = None
    tableOptions = tableDef.get('toptions', None)
    if tableOptions != None:
        cliCommandTable['toptions'] = tableOptions
        if tableOptions.get('parser', None) is None:
            # Add default parser: aos-std
            cliCommandTable['toptions']['parser'] = 'aos-std'
        log.debug('table: %s toptions: %s' % (tableName, cliCommandTable['toptions']))

    return cliCommandTable


def parseArCliField(cliCommandDef, fieldDef, mappings):
    cliCommandField = dict()

    # Field name
    cliCommandField['ename'] = None
    if 'name' in fieldDef:
        # Simple field
        fieldName = fieldDef['name']
        cliCommandField['name'] = fieldName
    else:
        # Eval field
        fieldName = fieldDef['ename']
        cliCommandField['name'] = fieldName
        e = compile(fieldName, fieldName, 'eval')
        cliCommandField['ename'] = e
        log.debug('adding: ename: %s: %s' % (fieldName, e))

    # Field group can be overriden
    fieldGroup = fieldDef.get('group', cliCommandDef['group'])
    cliCommandField['group'] = fieldGroup

    # Parameter assignment
    fieldP = fieldDef.get('P', None)
    if fieldP != None:
        cliCommandField['P'] = fieldP
        log.debug('adding: %s, P: %s' % (fieldName, fieldP))

    # Column value assignment
    fieldC = fieldDef.get('C', None)
    if fieldC != None:
        cliCommandField['C'] = fieldC
        log.debug('adding: %s, R: %s' % (fieldName, fieldC))

    # eval() assignment
    fieldEval = fieldDef.get('eval', None)
    if fieldEval != None:
        e = compile(fieldEval, fieldEval, 'eval')
        cliCommandField['eval'] = e
        log.debug('adding: %s, eval: %s' % (fieldName, e))

    # when condition
    cliCommandField['when'] = None
    fieldWhen = fieldDef.get('when', None)
    if fieldWhen != None:
        e = compile(fieldWhen, fieldWhen, 'eval')
        cliCommandField['when'] = e
        log.debug('adding: %s, when: %s' % (fieldName, e))

    # mapping (optional, default: None)
    fieldMapping = fieldDef.get('mapping', None)
    if fieldMapping != None:
        if cliCommandField['ename'] != None:
            # ename fields are not supported yet!
            log.error('ignoring mapping for ename: %s' % (fieldName))
        else:
            _updateMapping(mappings, cliCommandDef['document'], fieldName, fieldMapping)
            log.debug('adding: %s, mapping: %s' % (fieldName, fieldMapping))

    return cliCommandField


def _updateMapping(mappings, document, fieldName, fieldMapping):
    mappings[fieldName] = fieldMapping
    root = mappings.get('_', None)
    if root is None:
        root = dict()
        mappings['_'] = root
    fields = root.get(document, None)
    if fields is None:
        fields = dict()
        root[document] = fields
    _fieldMapping = fields.get(fieldName, None)
    if _fieldMapping is not None and _fieldMapping != fieldMapping:
        log.error("FATAL: conflicting mapping for: %s/%s/%s" % (fieldName, _fieldMapping, fieldMapping))
        exit(1)
    fields[fieldName] = fieldMapping


