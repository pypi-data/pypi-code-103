#!/usr/bin/env python3


# SAT plugin for Explicit Message Encryption
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.words.protocols.jabber import jid

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "Explicit Message Encryption",
    C.PI_IMPORT_NAME: "XEP-0380",
    C.PI_TYPE: "SEC",
    C.PI_PROTOCOLS: ["XEP-0380"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0380",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of Explicit Message Encryption"""),
}

NS_EME = "urn:xmpp:eme:0"
KNOWN_NAMESPACES = {
    "urn:xmpp:otr:0": "OTR",
    "jabber:x:encrypted": "Legacy OpenPGP",
    "urn:xmpp:openpgp:0": "OpenPGP for XMPP",
}


class XEP_0380(object):

    def __init__(self, host):
        self.host = host
        host.trigger.add("sendMessage", self._sendMessageTrigger)
        host.trigger.add("messageReceived", self._messageReceivedTrigger, priority=100)
        host.registerNamespace("eme", NS_EME)

    def _addEMEElement(self, mess_data, namespace, name):
        message_elt = mess_data['xml']
        encryption_elt = message_elt.addElement((NS_EME, 'encryption'))
        encryption_elt['namespace'] = namespace
        if name is not None:
            encryption_elt['name'] = name
        return mess_data

    def _sendMessageTrigger(self, client, mess_data, __, post_xml_treatments):
        encryption = mess_data.get(C.MESS_KEY_ENCRYPTION)
        if encryption is not None:
            namespace = encryption['plugin'].namespace
            if namespace not in KNOWN_NAMESPACES:
                name = encryption['plugin'].name
            else:
                name = None
            post_xml_treatments.addCallback(
                self._addEMEElement, namespace=namespace, name=name)
        return True

    def _messageReceivedTrigger(self, client, message_elt, post_treat):
        try:
            encryption_elt = next(message_elt.elements(NS_EME, 'encryption'))
        except StopIteration:
            return True

        namespace = encryption_elt['namespace']
        if namespace in client.encryption.getNamespaces():
            # message is encrypted and we can decrypt it
            return True

        name = KNOWN_NAMESPACES.get(namespace, encryption_elt.getAttribute("name"))

        # at this point, message is encrypted but we know that we can't decrypt it,
        # we need to notify the user
        sender_s = message_elt['from']
        to_jid = jid.JID(message_elt['from'])
        algorithm = "{} [{}]".format(name, namespace) if name else namespace
        log.warning(
            _("Message from {sender} is encrypted with {algorithm} and we can't "
              "decrypt it.".format(sender=message_elt['from'], algorithm=algorithm)))

        user_msg = D_(
            "User {sender} sent you an encrypted message (encrypted with {algorithm}), "
            "and we can't decrypt it.").format(sender=sender_s, algorithm=algorithm)

        extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
        client.feedback(to_jid, user_msg, extra)
        return False
