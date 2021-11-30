#!/usr/bin/env python3


# SAT plugin for Delayed Delivery (XEP-0334)
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

from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C

from sat.tools.common import data_format

from wokkel import disco, iwokkel

from twisted.words.protocols.jabber import xmlstream
from zope.interface import implementer
from textwrap import dedent


PLUGIN_INFO = {
    C.PI_NAME: "Message Processing Hints",
    C.PI_IMPORT_NAME: "XEP-0334",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0334"],
    C.PI_MAIN: "XEP_0334",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: D_("""Implementation of Message Processing Hints"""),
    C.PI_USAGE: dedent(
        D_(
            """\
             Frontends can use HINT_* constants in mess_data['extra'] in a serialized 'hints' dict.
             Internal plugins can use directly addHint([HINT_* constant]).
             Will set mess_data['extra']['history'] to 'skipped' when no store is requested and message is not saved in history."""
        )
    ),
}

NS_HINTS = "urn:xmpp:hints"


class XEP_0334(object):
    HINT_NO_PERMANENT_STORE = "no-permanent-store"
    HINT_NO_STORE = "no-store"
    HINT_NO_COPY = "no-copy"
    HINT_STORE = "store"
    HINTS = (HINT_NO_PERMANENT_STORE, HINT_NO_STORE, HINT_NO_COPY, HINT_STORE)

    def __init__(self, host):
        log.info(_("Message Processing Hints plugin initialization"))
        self.host = host
        host.trigger.add("sendMessage", self.sendMessageTrigger)
        host.trigger.add("messageReceived", self.messageReceivedTrigger, priority=-1000)

    def getHandler(self, client):
        return XEP_0334_handler()

    def addHint(self, mess_data, hint):
        if hint == self.HINT_NO_COPY and not mess_data["to"].resource:
            log.error(
                "{hint} can only be used with full jids! Ignoring it.".format(hint=hint)
            )
            return
        hints = mess_data.setdefault("hints", set())
        if hint in self.HINTS:
            hints.add(hint)
        else:
            log.error("Unknown hint: {}".format(hint))

    def addHintElements(self, message_elt, hints):
        """Add hints elements to message stanza

        @param message_elt(domish.Element): stanza where hints must be added
        @param hints(iterable(unicode)): hints to add
        """
        for hint in hints:
            message_elt.addElement((NS_HINTS, hint))

    def _sendPostXmlTreatment(self, mess_data):
        if "hints" in mess_data:
            self.addHintElements(mess_data["xml"], mess_data["hints"])
        return mess_data

    def sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments
    ):
        """Add the hints element to the message to be sent"""
        if "hints" in mess_data["extra"]:
            for hint in data_format.dict2iter("hints", mess_data["extra"], pop=True):
                self.addHint(hint)

        post_xml_treatments.addCallback(self._sendPostXmlTreatment)
        return True

    def _receivedSkipHistory(self, mess_data):
        mess_data["history"] = C.HISTORY_SKIP
        return mess_data

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        """Check for hints in the received message"""
        for elt in message_elt.elements():
            if elt.uri == NS_HINTS and elt.name in (
                self.HINT_NO_PERMANENT_STORE,
                self.HINT_NO_STORE,
            ):
                log.debug("history will be skipped for this message, as requested")
                post_treat.addCallback(self._receivedSkipHistory)
                break
        return True


@implementer(iwokkel.IDisco)
class XEP_0334_handler(xmlstream.XMPPHandler):

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_HINTS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
