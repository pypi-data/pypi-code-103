#!/usr/bin/env python3

# Libervia: an XMPP client
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

from OpenSSL import SSL
from zope.interface import implementer
from treq.client import HTTPClient
from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
from twisted.internet import reactor, ssl
from twisted.web import iweb
from twisted.web import client as http_client
from sat.core.log import getLogger


log = getLogger(__name__)


SSLError = SSL.Error


@implementer(IOpenSSLClientConnectionCreator)
class NoCheckConnectionCreator(object):
    def __init__(self, hostname, ctx):
        self._ctx = ctx

    def clientConnectionForTLS(self, tlsProtocol):
        context = self._ctx
        connection = SSL.Connection(context, None)
        connection.set_app_data(tlsProtocol)
        return connection


@implementer(iweb.IPolicyForHTTPS)
class NoCheckContextFactory:
    """Context factory which doesn't do TLS certificate check

    /!\\ it's obvisously a security flaw to use this class,
    and it should be used only with explicit agreement from the end used
    """

    def creatorForNetloc(self, hostname, port):
        log.warning(
            "TLS check disabled for {host} on port {port}".format(
                host=hostname, port=port
            )
        )
        certificateOptions = ssl.CertificateOptions(trustRoot=None)
        return NoCheckConnectionCreator(hostname, certificateOptions.getContext())


#: following treq doesn't check TLS, obviously it is unsecure and should not be used
#: without explicit warning
treq_client_no_ssl = HTTPClient(http_client.Agent(reactor, NoCheckContextFactory()))
