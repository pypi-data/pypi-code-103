#!/usr/bin/env python3

# SàT plugin for Jingle Message Initiation (XEP-0353)
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

from zope.interface import implementer
from twisted.internet import defer
from twisted.internet import reactor
from twisted.words.protocols.jabber import xmlstream, jid, error
from twisted.words.xish import domish
from wokkel import disco, iwokkel
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools import utils
from sat.tools import xml_tools

log = getLogger(__name__)


NS_JINGLE_MESSAGE = "urn:xmpp:jingle-message:0"

PLUGIN_INFO = {
    C.PI_NAME: "Jingle Message Initiation",
    C.PI_IMPORT_NAME: "XEP-0353",
    C.PI_TYPE: "XEP",
    C.PI_MODES: [C.PLUG_MODE_CLIENT],
    C.PI_PROTOCOLS: ["XEP-0353"],
    C.PI_DEPENDENCIES: ["XEP-0166"],
    C.PI_MAIN: "XEP_0353",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Jingle Message Initiation"""),
}


class XEP_0353:

    def __init__(self, host):
        log.info(_("plugin {name} initialization").format(name=PLUGIN_INFO[C.PI_NAME]))
        self.host = host
        host.registerNamespace("jingle-message", NS_JINGLE_MESSAGE)
        self._j = host.plugins["XEP-0166"]
        host.trigger.add("XEP-0166_initiate", self._onInitiateTrigger)
        host.trigger.add("messageReceived", self._onMessageReceived)

    def getHandler(self, client):
        return Handler()

    def profileConnecting(self, client):
        # mapping from session id to deferred used to wait for destinee answer
        client._xep_0353_pending_sessions = {}

    def buildMessageData(self, client, peer_jid, verb, session_id):
        mess_data = {
            'from': client.jid,
            'to': peer_jid,
            'uid': '',
            'message': {},
            'type': C.MESS_TYPE_CHAT,
            'subject': {},
            'extra': {}
        }
        client.generateMessageXML(mess_data)
        verb_elt = mess_data["xml"].addElement((NS_JINGLE_MESSAGE, verb))
        verb_elt["id"] = session_id
        return mess_data

    async def _onInitiateTrigger(self, client, session, contents):
        # FIXME: check that at least one resource of the peer_jid can handle the feature
        peer_jid = session['peer_jid']
        if peer_jid.resource:
            return True

        try:
            infos = await self.host.memory.disco.getInfos(client, peer_jid)
        except error.StanzaError as e:
            if e.condition == "service-unavailable":
                categories = {}
            else:
                raise e
        else:
            categories = {c for c, __ in infos.identities}
        if "component" in categories:
            # we don't use message initiation with components
            return True

        if peer_jid.userhostJID() not in client.roster:
            # if the contact is not in our roster, we need to send a directed presence
            # according to XEP-0353 §3.1
            await client.presence.available(peer_jid)

        mess_data = self.buildMessageData(client, peer_jid, "propose", session['id'])
        for content in contents:
            application, app_args, app_kwargs, content_name = self._j.getContentData(
                content)
            try:
                jingleDescriptionElt = application.handler.jingleDescriptionElt
            except AttributeError:
                log.debug(f"no jingleDescriptionElt set for {application.handler}")
                description_elt = domish.Element((content["app_ns"], "description"))
            else:
                description_elt = await utils.asDeferred(
                    jingleDescriptionElt,
                    client, session, content_name, *app_args, **app_kwargs
                )
        mess_data["xml"].propose.addChild(description_elt)
        response_d = defer.Deferred()
        # we wait for 2 min before cancelling the session init
        response_d.addTimeout(2*60, reactor)
        client._xep_0353_pending_sessions[session['id']] = response_d
        await client.sendMessageData(mess_data)
        try:
            accepting_jid = await response_d
        except defer.TimeoutError:
            log.warning(_(
                "Message initiation with {peer_jid} timed out"
            ).format(peer_jid=peer_jid))
        else:
            session["peer_jid"] = accepting_jid
        del client._xep_0353_pending_sessions[session['id']]
        return True

    async def _onMessageReceived(self, client, message_elt, post_treat):
        for elt in message_elt.elements():
            if elt.uri == NS_JINGLE_MESSAGE:
                if elt.name == "propose":
                    return await self._handlePropose(client, message_elt, elt)
                elif elt.name == "retract":
                    return self._handleRetract(client, message_elt, elt)
                elif elt.name == "proceed":
                    return self._handleProceed(client, message_elt, elt)
                elif elt.name == "accept":
                    return self._handleAccept(client, message_elt, elt)
                elif elt.name == "reject":
                    return self._handleAccept(client, message_elt, elt)
                else:
                    log.warning(f"invalid element: {elt.toXml}")
                    return True
        return True

    async def _handlePropose(self, client, message_elt, elt):
        peer_jid = jid.JID(message_elt["from"])
        session_id = elt["id"]
        if peer_jid.userhostJID() not in client.roster:
            app_ns = elt.description.uri
            try:
                application = self._j.getApplication(app_ns)
                human_name = getattr(application.handler, "human_name", application.name)
            except (exceptions.NotFound, AttributeError):
                if app_ns.startswith("urn:xmpp:jingle:apps:"):
                    human_name = app_ns[21:].split(":", 1)[0].replace('-', ' ').title()
                else:
                    splitted_ns = app_ns.split(':')
                    if len(splitted_ns) > 1:
                        human_name = splitted_ns[-2].replace('- ', ' ').title()
                    else:
                        human_name = app_ns

            confirm_msg = D_(
                "Somebody not in your contact list ({peer_jid}) wants to do a "
                '"{human_name}" session with you, this would leak your presence and '
                "possibly you IP (internet localisation), do you accept?"
            ).format(peer_jid=peer_jid, human_name=human_name)
            confirm_title = D_("Invitation from an unknown contact")
            accept = await xml_tools.deferConfirm(
                self.host, confirm_msg, confirm_title, profile=client.profile,
                action_extra={
                    "meta_type": C.META_TYPE_NOT_IN_ROSTER_LEAK,
                    "meta_session_id": session_id,
                    "meta_from_jid": peer_jid.full(),
                }
            )
            if not accept:
                mess_data = self.buildMessageData(
                    client, client.jid.userhostJID(), "reject", session_id)
                await client.sendMessageData(mess_data)
                # we don't sent anything to sender, to avoid leaking presence
                return False
            else:
                await client.presence.available(peer_jid)
        session_id = elt["id"]
        mess_data = self.buildMessageData(
            client, client.jid.userhostJID(), "accept", session_id)
        await client.sendMessageData(mess_data)
        mess_data = self.buildMessageData(
            client, peer_jid, "proceed", session_id)
        await client.sendMessageData(mess_data)
        return False

    def _handleRetract(self, client, message_elt, proceed_elt):
        log.warning("retract is not implemented yet")
        return False

    def _handleProceed(self, client, message_elt, proceed_elt):
        try:
            session_id = proceed_elt["id"]
        except KeyError:
            log.warning(f"invalid proceed element in message_elt: {message_elt}")
            return True
        try:
            response_d = client._xep_0353_pending_sessions[session_id]
        except KeyError:
            log.warning(
                _("no pending session found with id {session_id}, did it timed out?")
                .format(session_id=session_id)
            )
            return True

        response_d.callback(jid.JID(message_elt["from"]))
        return False

    def _handleAccept(self, client, message_elt, accept_elt):
        pass

    def _handleReject(self, client, message_elt, accept_elt):
        pass


@implementer(iwokkel.IDisco)
class Handler(xmlstream.XMPPHandler):

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_JINGLE_MESSAGE)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
