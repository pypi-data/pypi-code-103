#!/usr/bin/env python3

# SàT plugin to send invitations for file sharing
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
from sat.core.log import getLogger
from sat.core.xmpp import SatXMPPEntity
from sat.tools.common import data_format
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Sharing Invitation",
    C.PI_IMPORT_NAME: "FILE_SHARING_INVITATION",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0329", "INVITATION"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "FileSharingInvitation",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("Experimental handling of invitations for file sharing"),
}


class FileSharingInvitation:

    def __init__(self, host):
        log.info(_("File Sharing Invitation plugin initialization"))
        self.host = host
        ns_fis = host.getNamespace("fis")
        host.plugins["INVITATION"].registerNamespace(ns_fis, self.onInvitation)
        host.bridge.addMethod(
            "FISInvite",
            ".plugin",
            in_sign="ssssssss",
            out_sign="",
            method=self._sendFileSharingInvitation,
            async_=True
        )

    def _sendFileSharingInvitation(
            self, invitee_jid_s, service_s, repos_type=None, namespace=None, path=None,
            name=None, extra_s='', profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        invitee_jid = jid.JID(invitee_jid_s)
        service = jid.JID(service_s)
        extra = data_format.deserialise(extra_s)
        return defer.ensureDeferred(
            self.host.plugins["INVITATION"].sendFileSharingInvitation(
                client, invitee_jid, service, repos_type=repos_type or None,
                namespace=namespace or None, path=path or None, name=name or None,
                extra=extra)
        )

    def onInvitation(
        self,
        client: SatXMPPEntity,
        namespace: str,
        name: str,
        extra: dict,
        service: jid.JID,
        repos_type: str,
        sharing_ns: str,
        path: str
    ):
        if repos_type == "files":
            type_human = _("file sharing")
        elif repos_type == "photos":
            type_human = _("photo album")
        else:
            log.warning("Unknown repository type: {repos_type}".format(
                repos_type=repos_type))
            repos_type = "file"
            type_human = _("file sharing")
        log.info(_(
            '{profile} has received an invitation for a files repository ({type_human}) '
            'with namespace {sharing_ns!r} at path [{path}]').format(
            profile=client.profile, type_human=type_human, sharing_ns=sharing_ns,
                path=path)
            )
        return defer.ensureDeferred(
            self.host.plugins['LIST_INTEREST'].registerFileSharing(
                client, service, repos_type, sharing_ns, path, name, extra
            )
        )
