#!/usr/bin/env python3

# SàT plugin to manage invitations
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

from typing import Optional
from zope.interface import implementer
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from wokkel import disco, iwokkel
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core.xmpp import SatXMPPEntity
from sat.tools import utils

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Invitation",
    C.PI_IMPORT_NAME: "INVITATION",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "XEP-0329", "LIST_INTEREST"],
    C.PI_RECOMMENDATIONS: ["EMAIL_INVITATION"],
    C.PI_MAIN: "Invitation",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("Experimental handling of invitations"),
}

NS_INVITATION = "https://salut-a-toi/protocol/invitation:0"
INVITATION = '/message/invitation[@xmlns="{ns_invit}"]'.format(
    ns_invit=NS_INVITATION
)
NS_INVITATION_LIST = NS_INVITATION + "#list"


class Invitation(object):

    def __init__(self, host):
        log.info(_("Invitation plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        # map from namespace of the invitation to callback handling it
        self._ns_cb = {}

    def getHandler(self, client):
        return PubsubInvitationHandler(self)

    def registerNamespace(self, namespace, callback):
        """Register a callback for a namespace

        @param namespace(unicode): namespace handled
        @param callback(callbable): method handling the invitation
            For pubsub invitation, it will be called with following arguments:
                - client
                - name(unicode, None): name of the event
                - extra(dict): extra data
                - service(jid.JID): pubsub service jid
                - node(unicode): pubsub node
                - item_id(unicode, None): pubsub item id
                - item_elt(domish.Element): item of the invitation
            For file sharing invitation, it will be called with following arguments:
                - client
                - name(unicode, None): name of the repository
                - extra(dict): extra data
                - service(jid.JID): service jid of the file repository
                - repos_type(unicode): type of the repository, can be:
                    - files: generic file sharing
                    - photos: photos album
                - namespace(unicode, None): namespace of the repository
                - path(unicode, None): path of the repository
        @raise exceptions.ConflictError: this namespace is already registered
        """
        if namespace in self._ns_cb:
            raise exceptions.ConflictError(
                "invitation namespace {namespace} is already register with {callback}"
                .format(namespace=namespace, callback=self._ns_cb[namespace]))
        self._ns_cb[namespace] = callback

    def _generateBaseInvitation(self, client, invitee_jid, name, extra):
        """Generate common mess_data end invitation_elt

        @param invitee_jid(jid.JID): entitee to send invitation to
        @param name(unicode, None): name of the shared repository
        @param extra(dict, None): extra data, where key can be:
            - thumb_url: URL of a thumbnail
        @return (tuple[dict, domish.Element): mess_data and invitation_elt
        """
        mess_data = {
            "from": client.jid,
            "to": invitee_jid,
            "uid": "",
            "message": {},
            "type": C.MESS_TYPE_CHAT,
            "subject": {},
            "extra": {},
        }
        client.generateMessageXML(mess_data)
        invitation_elt = mess_data["xml"].addElement("invitation", NS_INVITATION)
        if name is not None:
            invitation_elt["name"] = name
        thumb_url = extra.get('thumb_url')
        if thumb_url:
            if not thumb_url.startswith('http'):
                log.warning(
                    "only http URLs are allowed for thumbnails, got {url}, ignoring"
                    .format(url=thumb_url))
            else:
                invitation_elt['thumb_url'] = thumb_url
        return mess_data, invitation_elt

    def sendPubsubInvitation(
        self,
        client: SatXMPPEntity,
        invitee_jid: jid.JID,
        service: jid.JID,
        node: str,
        item_id: Optional[str],
        name: Optional[str],
        extra: Optional[dict]
    ) -> None:
        """Send an pubsub invitation in a <message> stanza

        @param invitee_jid: entitee to send invitation to
        @param service: pubsub service
        @param node: pubsub node
        @param item_id: pubsub id
            None when the invitation is for a whole node
        @param name: see [_generateBaseInvitation]
        @param extra: see [_generateBaseInvitation]
        """
        if extra is None:
            extra = {}
        mess_data, invitation_elt = self._generateBaseInvitation(
            client, invitee_jid, name, extra)
        pubsub_elt = invitation_elt.addElement("pubsub")
        pubsub_elt["service"] = service.full()
        pubsub_elt["node"] = node
        if item_id is None:
            try:
                namespace = extra.pop("namespace")
            except KeyError:
                raise exceptions.DataError('"namespace" key is missing in "extra" data')
            node_data_elt = pubsub_elt.addElement("node_data")
            node_data_elt["namespace"] = namespace
            try:
                node_data_elt.addChild(extra["element"])
            except KeyError:
                pass
        else:
            pubsub_elt["item"] = item_id
        if "element" in extra:
            invitation_elt.addChild(extra.pop("element"))
        client.send(mess_data["xml"])

    async def sendFileSharingInvitation(
        self, client, invitee_jid, service, repos_type=None, namespace=None, path=None,
        name=None, extra=None
    ):
        """Send a file sharing invitation in a <message> stanza

        @param invitee_jid(jid.JID): entitee to send invitation to
        @param service(jid.JID): file sharing service
        @param repos_type(unicode, None): type of files repository, can be:
            - None, "files": files sharing
            - "photos": photos album
        @param namespace(unicode, None): namespace of the shared repository
        @param path(unicode, None): path of the shared repository
        @param name(unicode, None): see [_generateBaseInvitation]
        @param extra(dict, None): see [_generateBaseInvitation]
        """
        if extra is None:
            extra = {}
        li_plg = self.host.plugins["LIST_INTEREST"]
        li_plg.normaliseFileSharingService(client, service)

        # FIXME: not the best place to adapt permission, but it's necessary to check them
        #   for UX
        try:
            await self.host.plugins['XEP-0329'].affiliationsSet(
                client, service, namespace, path, {invitee_jid: "member"}
            )
        except Exception as e:
            log.warning(f"Can't set affiliation: {e}")

        if "thumb_url" not in extra:
            # we have no thumbnail, we check in our own list of interests if there is one
            try:
                item_id = li_plg.getFileSharingId(service, namespace, path)
                own_interest = await li_plg.get(client, item_id)
            except exceptions.NotFound:
                log.debug(
                    "no thumbnail found for file sharing interest at "
                    f"[{service}/{namespace}]{path}"
                )
            else:
                try:
                    extra['thumb_url'] = own_interest['thumb_url']
                except KeyError:
                    pass

        mess_data, invitation_elt = self._generateBaseInvitation(
            client, invitee_jid, name, extra)
        file_sharing_elt = invitation_elt.addElement("file_sharing")
        file_sharing_elt["service"] = service.full()
        if repos_type is not None:
            if repos_type not in ("files", "photos"):
                msg = "unknown repository type: {repos_type}".format(
                    repos_type=repos_type)
                log.warning(msg)
                raise exceptions.DateError(msg)
            file_sharing_elt["type"] = repos_type
        if namespace is not None:
            file_sharing_elt["namespace"] = namespace
        if path is not None:
            file_sharing_elt["path"] = path
        client.send(mess_data["xml"])

    async def _parsePubsubElt(self, client, pubsub_elt):
        try:
            service = jid.JID(pubsub_elt["service"])
            node = pubsub_elt["node"]
        except (RuntimeError, KeyError):
            raise exceptions.DataError("Bad invitation, ignoring")

        item_id = pubsub_elt.getAttribute("item")

        if item_id is not None:
            try:
                items, metadata = await self._p.getItems(
                    client, service, node, item_ids=[item_id]
                )
            except Exception as e:
                log.warning(_("Can't get item linked with invitation: {reason}").format(
                            reason=e))
            try:
                item_elt = items[0]
            except IndexError:
                log.warning(_("Invitation was linking to a non existing item"))
                raise exceptions.DataError

            try:
                namespace = item_elt.firstChildElement().uri
            except Exception as e:
                log.warning(_("Can't retrieve namespace of invitation: {reason}").format(
                    reason = e))
                raise exceptions.DataError

            args = [service, node, item_id, item_elt]
        else:
            try:
                node_data_elt = next(pubsub_elt.elements((NS_INVITATION, "node_data")))
            except StopIteration:
                raise exceptions.DataError("Bad invitation, ignoring")
            namespace = node_data_elt['namespace']
            args = [service, node, None, node_data_elt]

        return namespace, args

    async def _parseFileSharingElt(self, client, file_sharing_elt):
        try:
            service = jid.JID(file_sharing_elt["service"])
        except (RuntimeError, KeyError):
            log.warning(_("Bad invitation, ignoring"))
            raise exceptions.DataError
        repos_type = file_sharing_elt.getAttribute("type", "files")
        sharing_ns = file_sharing_elt.getAttribute("namespace")
        path = file_sharing_elt.getAttribute("path")
        args = [service, repos_type, sharing_ns, path]
        ns_fis = self.host.getNamespace("fis")
        return ns_fis, args

    async def onInvitation(self, message_elt, client):
        log.debug("invitation received [{profile}]".format(profile=client.profile))
        invitation_elt = message_elt.invitation

        name = invitation_elt.getAttribute("name")
        extra = {}
        if invitation_elt.hasAttribute("thumb_url"):
            extra['thumb_url'] = invitation_elt['thumb_url']

        for elt in invitation_elt.elements():
            if elt.uri != NS_INVITATION:
                log.warning("unexpected element: {xml}".format(xml=elt.toXml()))
                continue
            if elt.name == "pubsub":
                method = self._parsePubsubElt
            elif elt.name == "file_sharing":
                method = self._parseFileSharingElt
            else:
                log.warning("not implemented invitation element: {xml}".format(
                    xml = elt.toXml()))
                continue
            try:
                namespace, args = await method(client, elt)
            except exceptions.DataError:
                log.warning("Can't parse invitation element: {xml}".format(
                            xml = elt.toXml()))
                continue

            try:
                cb = self._ns_cb[namespace]
            except KeyError:
                log.warning(_(
                    'No handler for namespace "{namespace}", invitation ignored')
                    .format(namespace=namespace))
            else:
                await utils.asDeferred(cb, client, namespace, name, extra, *args)


@implementer(iwokkel.IDisco)
class PubsubInvitationHandler(XMPPHandler):

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            INVITATION,
            lambda message_elt: defer.ensureDeferred(
                self.plugin_parent.onInvitation(message_elt, client=self.parent)
            ),
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_INVITATION),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
