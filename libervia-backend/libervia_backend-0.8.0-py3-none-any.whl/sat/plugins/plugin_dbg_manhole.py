#!/usr/bin/env python3


# SAT plugin for debugging, using a manhole
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
from twisted.conch.insults import insults
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.internet import reactor, protocol, defer
from twisted.words.protocols.jabber import jid
from twisted.conch.manhole import ColoredManhole

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "Manhole debug plugin",
    C.PI_IMPORT_NAME: "manhole",
    C.PI_TYPE: "DEBUG",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "Manhole",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Debug plugin to have a telnet server"""),
}



class Manhole(object):

    def __init__(self, host):
        self.host = host
        port = int(host.memory.getConfig(None, "manhole_debug_dangerous_port_int", 0))
        if port:
            self.startManhole(port)

    def startManhole(self, port):
        log.warning(_("/!\\ Manhole debug server activated, be sure to not use it in "
                      "production, this is dangerous /!\\"))
        log.info(_("You can connect to manhole server using telnet on port {port}")
            .format(port=port))
        f = protocol.ServerFactory()
        namespace = {
            "host": self.host,
            "C": C,
            "jid": jid,
            "d": defer.ensureDeferred,
        }
        f.protocol = lambda: TelnetTransport(TelnetBootstrapProtocol,
                                             insults.ServerProtocol,
                                             ColoredManhole,
                                             namespace=namespace,
                                             )
        reactor.listenTCP(port, f)
