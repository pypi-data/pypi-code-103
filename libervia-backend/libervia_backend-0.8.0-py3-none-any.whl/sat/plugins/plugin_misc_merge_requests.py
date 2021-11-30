#!/usr/bin/env python3


# SAT plugin for Pubsub Schemas
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.tools.common import data_format
from sat.core.log import getLogger


log = getLogger(__name__)

APP_NS_MERGE_REQUESTS = 'org.salut-a-toi.merge_requests:0'

PLUGIN_INFO = {
    C.PI_NAME: _("Merge requests management"),
    C.PI_IMPORT_NAME: "MERGE_REQUESTS",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "XEP-0346", "LISTS", "TEXT_SYNTAXES"],
    C.PI_MAIN: "MergeRequests",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Merge requests management plugin""")
}

FIELD_DATA_TYPE = 'type'
FIELD_DATA = 'request_data'


MergeRequestHandler = namedtuple("MergeRequestHandler", ['name',
                                                         'handler',
                                                         'data_types',
                                                         'short_desc',
                                                         'priority'])


class MergeRequests(object):
    META_AUTHOR = 'author'
    META_EMAIL = 'email'
    META_TIMESTAMP = 'timestamp'
    META_HASH = 'hash'
    META_PARENT_HASH = 'parent_hash'
    META_COMMIT_MSG = 'commit_msg'
    META_DIFF = 'diff'
    # index of the diff in the whole data
    # needed to retrieve comments location
    META_DIFF_IDX = 'diff_idx'

    def __init__(self, host):
        log.info(_("Merge requests plugin initialization"))
        self.host = host
        self._s = self.host.plugins["XEP-0346"]
        self.namespace = self._s.getSubmittedNS(APP_NS_MERGE_REQUESTS)
        host.registerNamespace('merge_requests', self.namespace)
        self._p = self.host.plugins["XEP-0060"]
        self._t = self.host.plugins["LISTS"]
        self._handlers = {}
        self._handlers_list = []  # handlers sorted by priority
        self._type_handlers = {}  # data type => handler map
        host.bridge.addMethod("mergeRequestsGet", ".plugin",
                              in_sign='ssiassa{ss}s', out_sign='s',
                              method=self._get,
                              async_=True
                              )
        host.bridge.addMethod("mergeRequestSet", ".plugin",
                              in_sign='ssssa{sas}ssss', out_sign='s',
                              method=self._set,
                              async_=True)
        host.bridge.addMethod("mergeRequestsSchemaGet", ".plugin",
                              in_sign='sss', out_sign='s',
                              method=lambda service, nodeIdentifier, profile_key:
                                self._s._getUISchema(service,
                                                     nodeIdentifier,
                                                     default_node=self.namespace,
                                                     profile_key=profile_key),
                              async_=True)
        host.bridge.addMethod("mergeRequestParseData", ".plugin",
                              in_sign='ss', out_sign='aa{ss}',
                              method=self._parseData,
                              async_=True)
        host.bridge.addMethod("mergeRequestsImport", ".plugin",
                              in_sign='ssssa{ss}s', out_sign='',
                              method=self._import,
                              async_=True
                              )

    def register(self, name, handler, data_types, short_desc, priority=0):
        """register an merge request handler

        @param name(unicode): name of the handler
        @param handler(object): instance of the handler.
            It must have the following methods, which may all return a Deferred:
                - check(repository)->bool: True if repository can be handled
                - export(repository)->str: return export data, i.e. the patches
                - parse(export_data): parse report data and return a list of dict
                                      (1 per patch) with:
                    - title: title of the commit message (first line)
                    - body: body of the commit message
        @aram data_types(list[unicode]): data types that his handler can generate or parse
        """
        if name in self._handlers:
            raise exceptions.ConflictError(_("a handler with name {name} already "
                                             "exists!").format(name = name))
        self._handlers[name] = MergeRequestHandler(name,
                                                   handler,
                                                   data_types,
                                                   short_desc,
                                                   priority)
        self._handlers_list.append(name)
        self._handlers_list.sort(key=lambda name: self._handlers[name].priority)
        if isinstance(data_types, str):
            data_types = [data_types]
        for data_type in data_types:
            if data_type in self._type_handlers:
                log.warning(_('merge requests of type {type} are already handled by '
                              '{old_handler}, ignoring {new_handler}').format(
                                type = data_type,
                old_handler = self._type_handlers[data_type].name,
                new_handler = name))
                continue
            self._type_handlers[data_type] = self._handlers[name]

    def serialise(self, get_data):
        tickets_xmlui, metadata, items_patches = get_data
        tickets_xmlui_s, metadata = self._p.transItemsData((tickets_xmlui, metadata))
        return data_format.serialise({
            "items": tickets_xmlui_s,
            "metadata": metadata,
            "items_patches": items_patches,
        })

    def _get(self, service='', node='', max_items=10, item_ids=None, sub_id=None,
             extra_dict=None, profile_key=C.PROF_KEY_NONE):
        if extra_dict and 'parse' in extra_dict:
                extra_dict['parse'] = C.bool(extra_dict['parse'])
        client, service, node, max_items, extra, sub_id = self._s.prepareBridgeGet(
            service, node, max_items, sub_id, extra_dict, profile_key)
        d = self.get(client, service, node or None, max_items, item_ids, sub_id or None,
                     extra.rsm_request, extra.extra)
        d.addCallback(self.serialise)
        return d

    @defer.inlineCallbacks
    def get(self, client, service=None, node=None, max_items=None, item_ids=None,
            sub_id=None, rsm_request=None, extra=None):
        """Retrieve merge requests and convert them to XMLUI

        @param extra(XEP-0060.parse, None): can have following keys:
            - update(bool): if True, will return list of parsed request data
        other params are the same as for [TICKETS._get]
        @return (tuple[list[unicode], list[dict[unicode, unicode]])): tuple with
            - XMLUI of the tickets, like [TICKETS._get]
            - node metadata
            - list of parsed request data (if extra['parse'] is set, else empty list)
        """
        if not node:
            node = self.namespace
        if extra is None:
            extra = {}
        # XXX: Q&D way to get list for labels when displaying them, but text when we
        #      have to modify them
        if C.bool(extra.get('labels_as_list', C.BOOL_FALSE)):
            filters = {'labels': self._s.textbox2ListFilter}
        else:
            filters = {}
        tickets_xmlui, metadata = yield defer.ensureDeferred(
            self._s.getDataFormItems(
                client,
                service,
                node,
                max_items=max_items,
                item_ids=item_ids,
                sub_id=sub_id,
                rsm_request=rsm_request,
                extra=extra,
                form_ns=APP_NS_MERGE_REQUESTS,
                filters = filters)
        )
        parsed_patches = []
        if extra.get('parse', False):
            for ticket in tickets_xmlui:
                request_type = ticket.named_widgets[FIELD_DATA_TYPE].value
                request_data = ticket.named_widgets[FIELD_DATA].value
                parsed_data = yield self.parseData(request_type, request_data)
                parsed_patches.append(parsed_data)
        defer.returnValue((tickets_xmlui, metadata, parsed_patches))

    def _set(self, service, node, repository, method, values, schema=None, item_id=None,
             extra="", profile_key=C.PROF_KEY_NONE):
        client, service, node, schema, item_id, extra = self._s.prepareBridgeSet(
            service, node, schema, item_id, extra, profile_key)
        d = defer.ensureDeferred(
            self.set(
                client, service, node, repository, method, values, schema,
                item_id or None, extra, deserialise=True
            )
        )
        d.addCallback(lambda ret: ret or '')
        return d

    async def set(self, client, service, node, repository, method='auto', values=None,
            schema=None, item_id=None, extra=None, deserialise=False):
        """Publish a tickets

        @param service(None, jid.JID): Pubsub service to use
        @param node(unicode, None): Pubsub node to use
            None to use default tickets node
        @param repository(unicode): path to the repository where the code stands
        @param method(unicode): name of one of the registered handler,
                                or "auto" to try autodetection.
        other arguments are same as for [TICKETS.set]
        @return (unicode): id of the created item
        """
        if not node:
            node = self.namespace
        if values is None:
            values = {}
        update = extra.get('update', False)
        if not repository and not update:
            # in case of update, we may re-user former patches data
            # so repository is not mandatory
            raise exceptions.DataError(_("repository must be specified"))

        if FIELD_DATA in values:
            raise exceptions.DataError(_("{field} is set by backend, you must not set "
                                         "it in frontend").format(field = FIELD_DATA))

        if repository:
            if method == 'auto':
                for name in self._handlers_list:
                    handler = self._handlers[name].handler
                    can_handle = await handler.check(repository)
                    if can_handle:
                        log.info(_("{name} handler will be used").format(name=name))
                        break
                else:
                    log.warning(_("repository {path} can't be handled by any installed "
                                  "handler").format(
                        path = repository))
                    raise exceptions.NotFound(_("no handler for this repository has "
                                                "been found"))
            else:
                try:
                    handler = self._handlers[name].handler
                except KeyError:
                    raise exceptions.NotFound(_("No handler of this name found"))

            data = await handler.export(repository)
            if not data.strip():
                raise exceptions.DataError(_('export data is empty, do you have any '
                                             'change to send?'))

            if not values.get('title') or not values.get('body'):
                patches = await handler.parse(data, values.get(FIELD_DATA_TYPE))
                commits_msg = patches[-1][self.META_COMMIT_MSG]
                msg_lines = commits_msg.splitlines()
                if not values.get('title'):
                    values['title'] = msg_lines[0]
                if not values.get('body'):
                    ts = self.host.plugins['TEXT_SYNTAXES']
                    xhtml = await ts.convert(
                        '\n'.join(msg_lines[1:]),
                        syntax_from = ts.SYNTAX_TEXT,
                        syntax_to = ts.SYNTAX_XHTML,
                        profile = client.profile)
                    values['body'] = '<div xmlns="{ns}">{xhtml}</div>'.format(
                        ns=C.NS_XHTML, xhtml=xhtml)

            values[FIELD_DATA] = data

        item_id = await self._t.set(client, service, node, values, schema, item_id, extra,
                                    deserialise, form_ns=APP_NS_MERGE_REQUESTS)
        return item_id

    def _parseData(self, data_type, data):
        d = self.parseData(data_type, data)
        d.addCallback(lambda parsed_patches:
            {key: str(value) for key, value in parsed_patches.items()})
        return d

    def parseData(self, data_type, data):
        """Parse a merge request data according to type

        @param data_type(unicode): type of the data to parse
        @param data(unicode): data to parse
        @return(list[dict[unicode, unicode]]): parsed data
            key of dictionary are self.META_* or keys specifics to handler
        @raise NotFound: no handler can parse this data_type
        """
        try:
            handler = self._type_handlers[data_type]
        except KeyError:
            raise exceptions.NotFound(_('No handler can handle data type "{type}"')
                                      .format(type=data_type))
        return defer.maybeDeferred(handler.handler.parse, data, data_type)

    def _import(self, repository, item_id, service=None, node=None, extra=None,
                profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        d = self.import_request(client, repository, item_id, service, node or None,
                                extra=extra or None)
        return d

    @defer.inlineCallbacks
    def import_request(self, client, repository, item, service=None, node=None,
                       extra=None):
        """Import a merge request in specified directory

        @param repository(unicode): path to the repository where the code stands
        """
        if not node:
            node = self.namespace
        tickets_xmlui, metadata = yield defer.ensureDeferred(
            self._s.getDataFormItems(
                client,
                service,
                node,
                max_items=1,
                item_ids=[item],
                form_ns=APP_NS_MERGE_REQUESTS)
        )
        ticket_xmlui = tickets_xmlui[0]
        data = ticket_xmlui.named_widgets[FIELD_DATA].value
        data_type = ticket_xmlui.named_widgets[FIELD_DATA_TYPE].value
        try:
            handler = self._type_handlers[data_type]
        except KeyError:
            raise exceptions.NotFound(_('No handler found to import {data_type}')
                                      .format(data_type=data_type))
        log.info(_("Importing patch [{item_id}] using {name} handler").format(
            item_id = item,
            name = handler.name))
        yield handler.handler.import_(repository, data, data_type, item, service, node,
                                      extra)
