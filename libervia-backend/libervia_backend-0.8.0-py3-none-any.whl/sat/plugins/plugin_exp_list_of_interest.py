#!/usr/bin/env python3


# SAT plugin to detect language (experimental)
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.xmpp import SatXMPPEntity
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools.common import data_format
from sat.tools.common import uri
from wokkel import disco, iwokkel, pubsub
from zope.interface import implementer
from twisted.internet import defer
from twisted.words.protocols.jabber import error as jabber_error, jid
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.xish import domish

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "List of Interest",
    C.PI_IMPORT_NAME: "LIST_INTEREST",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "XEP-0329", "XEP-0106"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "ListInterest",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("Experimental handling of interesting XMPP locations"),
}

NS_LIST_INTEREST = "https://salut-a-toi/protocol/list-interest:0"


class ListInterest(object):
    namespace = NS_LIST_INTEREST

    def __init__(self, host):
        log.info(_("List of Interest plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        host.bridge.addMethod(
            "interestsList",
            ".plugin",
            in_sign="ssss",
            out_sign="aa{ss}",
            method=self._listInterests,
            async_=True,
        )
        host.bridge.addMethod(
            "interestsRegisterFileSharing",
            ".plugin",
            in_sign="sssssss",
            out_sign="",
            method=self._registerFileSharing,
            async_=True,
        )
        host.bridge.addMethod(
            "interestRetract",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._interestRetract,
            async_=True,
        )

    def getHandler(self, client):
        return ListInterestHandler(self)

    @defer.inlineCallbacks
    def createNode(self, client):
        try:
            # TODO: check auto-create, no need to create node first if available
            options = {self._p.OPT_ACCESS_MODEL: self._p.ACCESS_WHITELIST}
            yield self._p.createNode(
                client,
                client.jid.userhostJID(),
                nodeIdentifier=NS_LIST_INTEREST,
                options=options,
            )
        except jabber_error.StanzaError as e:
            if e.condition == "conflict":
                log.debug(_("requested node already exists"))

    @defer.inlineCallbacks
    def registerPubsub(self, client, namespace, service, node, item_id=None,
                       creator=False, name=None, element=None, extra=None):
        """Register an interesting element in personal list

        @param namespace(unicode): namespace of the interest
            this is used as a cache, to avoid the need to retrieve the item only to get
            its namespace
        @param service(jid.JID): target pubsub service
        @param node(unicode): target pubsub node
        @param item_id(unicode, None): target pubsub id
        @param creator(bool): True if client's profile is the creator of the node
            This is used a cache, to avoid the need to retrieve affiliations
        @param name(unicode, None): name of the interest
        @param element(domish.Element, None): element to attach
            may be used to cache some extra data
        @param extra(dict, None): extra data, key can be:
            - thumb_url: http(s) URL of a thumbnail
        """
        if extra is None:
            extra = {}
        yield self.createNode(client)
        interest_elt = domish.Element((NS_LIST_INTEREST, "interest"))
        interest_elt["namespace"] = namespace
        if name is not None:
            interest_elt['name'] = name
        thumb_url = extra.get('thumb_url')
        if thumb_url:
            interest_elt['thumb_url'] = thumb_url
        pubsub_elt = interest_elt.addElement("pubsub")
        pubsub_elt["service"] = service.full()
        pubsub_elt["node"] = node
        if item_id is not None:
            pubsub_elt["item"] = item_id
        if creator:
            pubsub_elt["creator"] = C.BOOL_TRUE
        if element is not None:
            pubsub_elt.addChild(element)
        uri_kwargs = {
            "path": service.full(),
            "node": node
        }
        if item_id:
            uri_kwargs['id'] = item_id
        interest_uri = uri.buildXMPPUri("pubsub", **uri_kwargs)
        # we use URI of the interest as item id to avoid duplicates
        item_elt = pubsub.Item(interest_uri, payload=interest_elt)
        yield self._p.publish(
            client, client.jid.userhostJID(), NS_LIST_INTEREST, items=[item_elt]
        )

    def _registerFileSharing(
        self, service, repos_type, namespace, path, name, extra_raw,
        profile
    ):
        client = self.host.getClient(profile)
        extra = data_format.deserialise(extra_raw)

        return defer.ensureDeferred(self.registerFileSharing(
            client, jid.JID(service), repos_type or None, namespace or None, path or None,
            name or None, extra
        ))

    def normaliseFileSharingService(self, client, service):
        # FIXME: Q&D fix as the bare file sharing service JID will lead to user own
        #   repository, which thus would not be the same for the host and the guest.
        #   By specifying the user part, we for the use of the host repository.
        #   A cleaner way should be implemented
        if service.user is None:
            service.user = self.host.plugins['XEP-0106'].escape(client.jid.user)

    def getFileSharingId(self, service, namespace, path):
        return f"{service}_{namespace or ''}_{path or ''}"

    async def registerFileSharing(
            self, client, service, repos_type=None, namespace=None, path=None, name=None,
            extra=None):
        """Register an interesting file repository in personal list

        @param service(jid.JID): service of the file repository
        @param repos_type(unicode): type of the repository
        @param namespace(unicode, None): namespace of the repository
        @param path(unicode, None): path of the repository
        @param name(unicode, None): name of the repository
        @param extra(dict, None): same as [registerPubsub]
        """
        if extra is None:
            extra = {}
        self.normaliseFileSharingService(client, service)
        await self.createNode(client)
        item_id = self.getFileSharingId(service, namespace, path)
        interest_elt = domish.Element((NS_LIST_INTEREST, "interest"))
        interest_elt["namespace"] = self.host.getNamespace("fis")
        if name is not None:
            interest_elt['name'] = name
        thumb_url = extra.get('thumb_url')
        if thumb_url:
            interest_elt['thumb_url'] = thumb_url

        file_sharing_elt = interest_elt.addElement("file_sharing")
        file_sharing_elt["service"] = service.full()
        if repos_type is not None:
            file_sharing_elt["type"] = repos_type
        if namespace is not None:
            file_sharing_elt["namespace"] = namespace
        if path is not None:
            file_sharing_elt["path"] = path
        item_elt = pubsub.Item(item_id, payload=interest_elt)
        await self._p.publish(
            client, client.jid.userhostJID(), NS_LIST_INTEREST, items=[item_elt]
        )

    def _listInterestsSerialise(self, interests_data):
        interests = []
        for item_elt in interests_data[0]:
            interest_data = {"id": item_elt['id']}
            interest_elt = item_elt.interest
            if interest_elt.hasAttribute('namespace'):
                interest_data['namespace'] = interest_elt.getAttribute('namespace')
            if interest_elt.hasAttribute('name'):
                interest_data['name'] = interest_elt.getAttribute('name')
            if interest_elt.hasAttribute('thumb_url'):
                interest_data['thumb_url'] = interest_elt.getAttribute('thumb_url')
            elt = interest_elt.firstChildElement()
            if elt.uri != NS_LIST_INTEREST:
                log.warning("unexpected child element, ignoring: {xml}".format(
                    xml = elt.toXml()))
                continue
            if elt.name == 'pubsub':
                interest_data.update({
                    "type": "pubsub",
                    "service": elt['service'],
                    "node": elt['node'],
                })
                for attr in ('item', 'creator'):
                    if elt.hasAttribute(attr):
                        interest_data[attr] = elt[attr]
            elif elt.name == 'file_sharing':
                interest_data.update({
                    "type": "file_sharing",
                    "service": elt['service'],
                })
                if elt.hasAttribute('type'):
                    interest_data['subtype'] = elt['type']
                for attr in ('files_namespace', 'path'):
                    if elt.hasAttribute(attr):
                        interest_data[attr] = elt[attr]
            else:
                log.warning("unknown element, ignoring: {xml}".format(xml=elt.toXml()))
                continue
            interests.append(interest_data)

        return interests

    def _listInterests(self, service, node, namespace, profile):
        service = jid.JID(service) if service else None
        node = node or None
        namespace = namespace or None
        client = self.host.getClient(profile)
        d = self.listInterests(client, service, node, namespace)
        d.addCallback(self._listInterestsSerialise)
        return d

    @defer.inlineCallbacks
    def listInterests(self, client, service=None, node=None, namespace=None):
        """Retrieve list of interests

        @param service(jid.JID, None): service to use
            None to use own PEP
        @param node(unicode, None): node to use
            None to use default node
        @param namespace(unicode, None): filter interests of this namespace
            None to retrieve all interests
        @return: same as [XEP_0060.getItems]
        """
        # TODO: if a MAM filter were available, it would improve performances
        if not node:
            node = NS_LIST_INTEREST
        items, metadata = yield self._p.getItems(client, service, node)
        if namespace is not None:
            filtered_items = []
            for item in items:
                try:
                    interest_elt = next(item.elements(NS_LIST_INTEREST, "interest"))
                except StopIteration:
                    log.warning(_("Missing interest element: {xml}").format(
                        xml=item.toXml()))
                    continue
                if interest_elt.getAttribute("namespace") == namespace:
                    filtered_items.append(item)
            items = filtered_items

        defer.returnValue((items, metadata))

    def _interestRetract(self, service_s, item_id, profile_key):
        d = self._p._retractItem(
            service_s, NS_LIST_INTEREST, item_id, True, profile_key)
        d.addCallback(lambda __: None)
        return d

    async def get(self, client: SatXMPPEntity, item_id: str) -> dict:
        """Retrieve a specific interest in profile's list"""
        items_data = await self._p.getItems(client, None, NS_LIST_INTEREST, item_ids=[item_id])
        try:
            return self._listInterestsSerialise(items_data)[0]
        except IndexError:
            raise exceptions.NotFound


@implementer(iwokkel.IDisco)
class ListInterestHandler(XMPPHandler):

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_LIST_INTEREST),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
