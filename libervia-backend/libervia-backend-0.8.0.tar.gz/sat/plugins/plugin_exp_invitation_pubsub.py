#!/usr/bin/env python3

# SàT plugin to send invitations for Pubsub
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
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core.xmpp import SatXMPPEntity
from sat.tools import utils
from sat.tools.common import data_format

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Pubsub Invitation",
    C.PI_IMPORT_NAME: "PUBSUB_INVITATION",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060", "INVITATION"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "PubsubInvitation",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("Invitations for pubsub based features"),
}


class PubsubInvitation:

    def __init__(self, host):
        log.info(_("Pubsub Invitation plugin initialization"))
        self.host = host
        self._p = host.plugins["XEP-0060"]
        # namespace to handler map
        self._ns_handler = {}
        host.bridge.addMethod(
            "psInvite",
            ".plugin",
            in_sign="sssssss",
            out_sign="",
            method=self._sendPubsubInvitation,
            async_=True
        )

    def register(
        self,
        namespace: str,
        handler
    ) -> None:
        self._ns_handler[namespace] = handler
        self.host.plugins["INVITATION"].registerNamespace(namespace, self.onInvitation)

    def _sendPubsubInvitation(
            self, invitee_jid_s, service_s, node, item_id=None,
            name=None, extra_s='', profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        invitee_jid = jid.JID(invitee_jid_s)
        service = jid.JID(service_s)
        extra = data_format.deserialise(extra_s)
        return defer.ensureDeferred(
            self.invite(
                client,
                invitee_jid,
                service,
                node,
                item_id or None,
                name=name or None,
                extra=extra
            )
        )

    async def invite(
        self,
        client: SatXMPPEntity,
        invitee_jid: jid.JID,
        service: jid.JID,
        node: str,
        item_id: Optional[str] = None,
        name: str = '',
        extra: Optional[dict] = None,
    ) -> None:
        if extra is None:
            extra = {}
        else:
            namespace = extra.get("namespace")
            if namespace:
                try:
                    handler = self._ns_handler[namespace]
                    preflight = handler.invitePreflight
                except KeyError:
                    pass
                except AttributeError:
                    log.debug(f"no invitePreflight method found for {namespace!r}")
                else:
                    await utils.asDeferred(
                        preflight,
                        client, invitee_jid, service, node, item_id, name, extra
                    )
            if item_id is None:
                item_id = extra.pop("default_item_id", None)

        # we authorize our invitee to see the nodes of interest
        await self._p.setNodeAffiliations(client, service, node, {invitee_jid: "member"})
        log.debug(f"affiliation set on {service}'s {node!r} node")

        # now we send the invitation
        self.host.plugins["INVITATION"].sendPubsubInvitation(
            client,
            invitee_jid,
            service,
            node,
            item_id,
            name=name or None,
            extra=extra
        )

    async def onInvitation(
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
        if extra is None:
            extra = {}
        try:
            handler = self._ns_handler[namespace]
            preflight = handler.onInvitationPreflight
        except KeyError:
            pass
        except AttributeError:
            log.debug(f"no onInvitationPreflight method found for {namespace!r}")
        else:
            await utils.asDeferred(
                preflight,
                client, namespace, name, extra, service, node, item_id, item_elt
            )
            if item_id is None:
                item_id = extra.pop("default_item_id", None)
        creator = extra.pop("creator", False)
        element = extra.pop("element", None)
        if not name:
            name = extra.pop("name", "")

        return self.host.plugins['LIST_INTEREST'].registerPubsub(
            client, namespace, service, node, item_id, creator,
            name, element, extra)
