#!/usr/bin/env python3

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

import shortuuid
from typing import List, Tuple, Optional
from twisted.internet import defer
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from sat.core.i18n import _, D_
from sat.core.xmpp import SatXMPPEntity
from sat.core.constants import Const as C
from sat.tools import xml_tools
from sat.tools.common import uri
from sat.tools.common import data_format
from sat.core.log import getLogger

log = getLogger(__name__)

# XXX: this plugin was formely named "tickets", thus the namespace keeps this
# name
APP_NS_TICKETS = "org.salut-a-toi.tickets:0"
NS_TICKETS_TYPE = "org.salut-a-toi.tickets#type:0"

PLUGIN_INFO = {
    C.PI_NAME: _("Pubsub Lists"),
    C.PI_IMPORT_NAME: "LISTS",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "XEP-0346", "XEP-0277", "IDENTITY",
                        "PUBSUB_INVITATION"],
    C.PI_MAIN: "PubsubLists",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Pubsub lists management plugin"""),
}

TEMPLATES = {
    "todo": {
        "name": D_("TODO List"),
        "icon": "check",
        "fields": [
            {"name": "title"},
            {"name": "author"},
            {"name": "created"},
            {"name": "updated"},
            {"name": "time_limit"},
            {"name": "labels", "type": "text-multi"},
            {
                "name": "status",
                "label": D_("status"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("to do"),
                        "value": "todo"
                    },
                    {
                        "label": D_("in progress"),
                        "value": "in_progress"
                    },
                    {
                        "label": D_("done"),
                        "value": "done"
                    },
                ],
                "value": "todo"
            },
            {
                "name": "priority",
                "label": D_("priority"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("major"),
                        "value": "major"
                    },
                    {
                        "label": D_("normal"),
                        "value": "normal"
                    },
                    {
                        "label": D_("minor"),
                        "value": "minor"
                    },
                ],
                "value": "normal"
            },
            {"name": "body", "type": "xhtml"},
            {"name": "comments_uri"},
        ]
    },
    "grocery": {
        "name": D_("Grocery List"),
        "icon": "basket",
        "fields": [
            {"name": "name", "label": D_("name")},
            {"name": "quantity", "label": D_("quantity")},
            {
                "name": "status",
                "label": D_("status"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("to buy"),
                        "value": "to_buy"
                    },
                    {
                        "label": D_("bought"),
                        "value": "bought"
                    },
                ],
                "value": "to_buy"
            },
        ]
    },
    "tickets": {
        "name": D_("Tickets"),
        "icon": "clipboard",
        "fields": [
            {"name": "title"},
            {"name": "author"},
            {"name": "created"},
            {"name": "updated"},
            {"name": "labels", "type": "text-multi"},
            {
                "name": "type",
                "label": D_("type"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("bug"),
                        "value": "bug"
                    },
                    {
                        "label": D_("feature request"),
                        "value": "feature"
                    },
                ],
                "value": "bug"
            },
            {
                "name": "status",
                "label": D_("status"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("queued"),
                        "value": "queued"
                    },
                    {
                        "label": D_("started"),
                        "value": "started"
                    },
                    {
                        "label": D_("review"),
                        "value": "review"
                    },
                    {
                        "label": D_("closed"),
                        "value": "closed"
                    },
                ],
                "value": "queued"
            },
            {
                "name": "priority",
                "label": D_("priority"),
                "type": "list-single",
                "options": [
                    {
                        "label": D_("major"),
                        "value": "major"
                    },
                    {
                        "label": D_("normal"),
                        "value": "normal"
                    },
                    {
                        "label": D_("minor"),
                        "value": "minor"
                    },
                ],
                "value": "normal"
            },
            {"name": "body", "type": "xhtml"},
            {"name": "comments_uri"},
        ]
    }
}


class PubsubLists:

    def __init__(self, host):
        log.info(_("Pubsub lists plugin initialization"))
        self.host = host
        self._s = self.host.plugins["XEP-0346"]
        self.namespace = self._s.getSubmittedNS(APP_NS_TICKETS)
        host.registerNamespace("tickets", APP_NS_TICKETS)
        host.registerNamespace("tickets_type", NS_TICKETS_TYPE)
        self.host.plugins["PUBSUB_INVITATION"].register(
            APP_NS_TICKETS, self
        )
        self._p = self.host.plugins["XEP-0060"]
        self._m = self.host.plugins["XEP-0277"]
        host.bridge.addMethod(
            "listGet",
            ".plugin",
            in_sign="ssiassa{ss}s",
            out_sign="s",
            method=lambda service, node, max_items, items_ids, sub_id, extra, profile_key:
                self._s._get(
                service,
                node,
                max_items,
                items_ids,
                sub_id,
                extra,
                default_node=self.namespace,
                form_ns=APP_NS_TICKETS,
                filters={
                    "author": self._s.valueOrPublisherFilter,
                    "created": self._s.dateFilter,
                    "updated": self._s.dateFilter,
                    "time_limit": self._s.dateFilter,
                },
                profile_key=profile_key),
            async_=True,
        )
        host.bridge.addMethod(
            "listSet",
            ".plugin",
            in_sign="ssa{sas}ssss",
            out_sign="s",
            method=self._set,
            async_=True,
        )
        host.bridge.addMethod(
            "listDeleteItem",
            ".plugin",
            in_sign="sssbs",
            out_sign="",
            method=self._delete,
            async_=True,
        )
        host.bridge.addMethod(
            "listSchemaGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=lambda service, nodeIdentifier, profile_key: self._s._getUISchema(
                service, nodeIdentifier, default_node=self.namespace,
                profile_key=profile_key),
            async_=True,
        )
        host.bridge.addMethod(
            "listsList",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._listsList,
            async_=True,
        )
        host.bridge.addMethod(
            "listTemplatesNamesGet",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._getTemplatesNames,
        )
        host.bridge.addMethod(
            "listTemplateGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._getTemplate,
        )
        host.bridge.addMethod(
            "listTemplateCreate",
            ".plugin",
            in_sign="ssss",
            out_sign="(ss)",
            method=self._createTemplate,
            async_=True,
        )

    async def onInvitationPreflight(
        self,
        client: SatXMPPEntity,
        namespace: str,
        name: str,
        extra: dict,
        service: jid.JID,
        node: str,
        item_id: Optional[str],
        item_elt: domish.Element
    ) -> None:
        try:
            schema = await self._s.getSchemaForm(client, service, node)
        except Exception as e:
            log.warning(f"Can't retrive node schema as {node!r} [{service}]: {e}")
        else:
            try:
                field_type = schema[NS_TICKETS_TYPE]
            except KeyError:
                log.debug("no type found in list schema")
            else:
                list_elt = extra["element"] = domish.Element((APP_NS_TICKETS, "list"))
                list_elt["type"] = field_type

    def _set(self, service, node, values, schema=None, item_id=None, extra='',
             profile_key=C.PROF_KEY_NONE):
        client, service, node, schema, item_id, extra = self._s.prepareBridgeSet(
            service, node, schema, item_id, extra, profile_key
        )
        d = defer.ensureDeferred(self.set(
            client, service, node, values, schema, item_id, extra, deserialise=True
        ))
        d.addCallback(lambda ret: ret or "")
        return d

    async def set(
        self, client, service, node, values, schema=None, item_id=None, extra=None,
        deserialise=False, form_ns=APP_NS_TICKETS
    ):
        """Publish a tickets

        @param node(unicode, None): Pubsub node to use
            None to use default tickets node
        @param values(dict[key(unicode), [iterable[object]|object]]): values of the ticket

            if value is not iterable, it will be put in a list
            'created' and 'updated' will be forced to current time:
                - 'created' is set if item_id is None, i.e. if it's a new ticket
                - 'updated' is set everytime
        @param extra(dict, None): same as for [XEP-0060.sendItem] with additional keys:
            - update(bool): if True, get previous item data to merge with current one
                if True, item_id must be set
        other arguments are same as for [self._s.sendDataFormItem]
        @return (unicode): id of the created item
        """
        if not node:
            node = self.namespace

        if not item_id:
            comments_service = await self._m.getCommentsService(client, service)

            # we need to use uuid for comments node, because we don't know item id in
            # advance (we don't want to set it ourselves to let the server choose, so we
            # can have a nicer id if serial ids is activated)
            comments_node = self._m.getCommentsNode(
                node + "_" + str(shortuuid.uuid())
            )
            options = {
                self._p.OPT_ACCESS_MODEL: self._p.ACCESS_OPEN,
                self._p.OPT_PERSIST_ITEMS: 1,
                self._p.OPT_MAX_ITEMS: -1,
                self._p.OPT_DELIVER_PAYLOADS: 1,
                self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
                self._p.OPT_PUBLISH_MODEL: self._p.ACCESS_OPEN,
            }
            await self._p.createNode(client, comments_service, comments_node, options)
            values["comments_uri"] = uri.buildXMPPUri(
                "pubsub",
                subtype="microblog",
                path=comments_service.full(),
                node=comments_node,
            )

        return await self._s.set(
            client, service, node, values, schema, item_id, extra, deserialise, form_ns
        )

    def _delete(
        self, service_s, nodeIdentifier, itemIdentifier, notify, profile_key
    ):
        client = self.host.getClient(profile_key)
        return defer.ensureDeferred(self.delete(
            client,
            jid.JID(service_s) if service_s else None,
            nodeIdentifier,
            itemIdentifier,
            notify
        ))

    async def delete(
        self,
        client: SatXMPPEntity,
        service: Optional[jid.JID],
        node: Optional[str],
        itemIdentifier: str,
        notify: Optional[bool] = None
    ) -> None:
        if not node:
            node = self.namespace
        return await self._p.retractItems(
            service, node, (itemIdentifier,), notify, client.profile
        )

    def _listsList(self, service, node, profile):
        service = jid.JID(service) if service else None
        node = node or None
        client = self.host.getClient(profile)
        d = defer.ensureDeferred(self.listsList(client, service, node))
        d.addCallback(data_format.serialise)
        return d

    async def listsList(
        self, client, service: Optional[jid.JID], node: Optional[str]=None
    ) -> List[dict]:
        """Retrieve list of pubsub lists registered in personal interests

        @return list: list of lists metadata
        """
        items, metadata = await self.host.plugins['LIST_INTEREST'].listInterests(
            client, service, node, namespace=APP_NS_TICKETS)
        lists = []
        for item in items:
            interest_elt = item.interest
            if interest_elt is None:
                log.warning(f"invalid interest for {client.profile}: {item.toXml}")
                continue
            if interest_elt.getAttribute("namespace") != APP_NS_TICKETS:
                continue
            pubsub_elt = interest_elt.pubsub
            list_data = {
                "id": item["id"],
                "name": interest_elt["name"],
                "service": pubsub_elt["service"],
                "node": pubsub_elt["node"],
                "creator": C.bool(pubsub_elt.getAttribute("creator", C.BOOL_FALSE)),
            }
            try:
                list_elt = next(pubsub_elt.elements(APP_NS_TICKETS, "list"))
            except StopIteration:
                pass
            else:
                list_type = list_data["type"] = list_elt["type"]
                if list_type in TEMPLATES:
                    list_data["icon_name"] = TEMPLATES[list_type]["icon"]
            lists.append(list_data)

        return lists

    def _getTemplatesNames(self, language, profile):
        client = self.host.getClient(profile)
        return data_format.serialise(self.getTemplatesNames(client, language))

    def getTemplatesNames(self, client, language: str) -> list:
        """Retrieve well known list templates"""

        templates = [{"id": tpl_id, "name": d["name"], "icon": d["icon"]}
                     for tpl_id, d in TEMPLATES.items()]
        return templates

    def _getTemplate(self, name, language, profile):
        client = self.host.getClient(profile)
        return data_format.serialise(self.getTemplate(client, name, language))

    def getTemplate(self, client, name: str, language: str) -> dict:
        """Retrieve a well known template"""
        return TEMPLATES[name]

    def _createTemplate(self, template_id, name, access_model, profile):
        client = self.host.getClient(profile)
        d = defer.ensureDeferred(self.createTemplate(
            client, template_id, name, access_model
        ))
        d.addCallback(lambda node_data: (node_data[0].full(), node_data[1]))
        return d

    async def createTemplate(
        self, client, template_id: str, name: str, access_model: str
    ) -> Tuple[jid.JID, str]:
        """Create a list from a template"""
        name = name.strip()
        if not name:
            name = shortuuid.uuid()
        fields = TEMPLATES[template_id]["fields"].copy()
        fields.insert(
            0,
            {"type": "hidden", "name": NS_TICKETS_TYPE, "value": template_id}
        )
        schema = xml_tools.dataDict2dataForm(
            {"namespace": APP_NS_TICKETS, "fields": fields}
        ).toElement()

        service = client.jid.userhostJID()
        node = self._s.getSubmittedNS(f"{APP_NS_TICKETS}_{name}")
        options = {
            self._p.OPT_ACCESS_MODEL: access_model,
        }
        if template_id == "grocery":
            # for grocery list, we want all publishers to be able to set all items
            # XXX: should node options be in TEMPLATE?
            options[self._p.OPT_OVERWRITE_POLICY] = self._p.OWPOL_ANY_PUB
        await self._p.createNode(client, service, node, options)
        await self._s.setSchema(client, service, node, schema)
        list_elt = domish.Element((APP_NS_TICKETS, "list"))
        list_elt["type"] = template_id
        try:
            await self.host.plugins['LIST_INTEREST'].registerPubsub(
                client, APP_NS_TICKETS, service, node, creator=True,
                name=name, element=list_elt)
        except Exception as e:
            log.warning(f"Can't add list to interests: {e}")
        return service, node
