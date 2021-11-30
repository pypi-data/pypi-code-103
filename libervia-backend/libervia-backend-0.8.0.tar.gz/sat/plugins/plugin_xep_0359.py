#!/usr/bin/env python3


# SAT plugin for Message Archive Management (XEP-0359)
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

import uuid
from zope.interface import implementer
from twisted.words.protocols.jabber import xmlstream
from wokkel import disco
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Unique and Stable Stanza IDs",
    C.PI_IMPORT_NAME: "XEP-0359",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0359"],
    C.PI_MAIN: "XEP_0359",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Unique and Stable Stanza IDs"""),
}

NS_SID = "urn:xmpp:sid:0"


class XEP_0359(object):

    def __init__(self, host):
        log.info(_("Unique and Stable Stanza IDs plugin initialization"))
        self.host = host
        host.registerNamespace("stanza_id", NS_SID)
        host.trigger.add("message_parse", self._message_parseTrigger)

    def _message_parseTrigger(self, client, message_elt, mess_data):
        """Check if message has a stanza-id"""
        stanza_id = self.getStanzaId(message_elt, client.jid.userhostJID())
        if stanza_id is not None:
            mess_data['extra']['stanza_id'] = stanza_id
        return True

    def getStanzaId(self, element, by):
        """Return stanza-id if found in element

        @param element(domish.Element): element to parse
        @param by(jid.JID): entity which should have set a stanza-id
        @return (unicode, None): stanza-id if found
        """
        stanza_id = None
        for stanza_elt in element.elements(NS_SID, "stanza-id"):
            if stanza_elt.getAttribute("by") == by.full():
                if stanza_id is not None:
                    # we must not have more than one element (§3 #4)
                    raise exceptions.DataError(
                        "More than one corresponding stanza-id found!")
                stanza_id = stanza_elt.getAttribute("id")
                # we don't break to be sure that there is no more than one element
                # with this "by" attribute

        return stanza_id

    def addStanzaId(self, client, element, stanza_id, by=None):
        """Add a <stanza-id/> to a stanza

        @param element(domish.Element): stanza where the <stanza-id/> must be added
        @param stanza_id(unicode): id to use
        @param by(jid.JID, None): jid to use or None to use client.jid
        """
        sid_elt = element.addElement((NS_SID, "stanza-id"))
        sid_elt["by"] = client.jid.userhost() if by is None else by.userhost()
        sid_elt["id"] = stanza_id

    def getOriginId(self, element):
        """Return origin-id if found in element

        @param element(domish.Element): element to parse
        @return (unicode, None): origin-id if found
        """
        try:
            origin_elt = next(element.elements(NS_SID, "origin-id"))
        except StopIteration:
            return None
        else:
            return origin_elt.getAttribute("id")

    def addOriginId(self, element, origin_id=None):
        """Add a <origin-id/> to a stanza

        @param element(domish.Element): stanza where the <origin-id/> must be added
        @param origin_id(str): id to use, None to automatically generate
        @return (str): origin_id
        """
        if origin_id is None:
            origin_id = str(uuid.uuid4())
        sid_elt = element.addElement((NS_SID, "origin-id"))
        sid_elt["id"] = origin_id
        return origin_id

    def getHandler(self, client):
        return XEP_0359_handler()


@implementer(disco.IDisco)
class XEP_0359_handler(xmlstream.XMPPHandler):

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SID)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
