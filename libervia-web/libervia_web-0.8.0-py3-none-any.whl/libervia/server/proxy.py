#!/usr/bin/env python3

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2021 Jérôme Poisson <goffi@goffi.org>

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
from twisted.web import proxy
from twisted.python.compat import urlquote
from twisted.internet import address
from sat.core.log import getLogger
from libervia.server.constants import Const as C

log = getLogger(__name__)



class SatProxyClient(proxy.ProxyClient):

    def handleHeader(self, key, value):
        if key.lower() == b"x-frame-options":
            value = b"sameorigin"
        elif key.lower() == b"content-security-policy":
            value = value.replace(b"frame-ancestors 'none'", b"frame-ancestors 'self'")

        super().handleHeader(key, value)


class SatProxyClientFactory(proxy.ProxyClientFactory):
    protocol = SatProxyClient


class SatReverseProxyResource(proxy.ReverseProxyResource):
    """Resource Proxy rewritting headers to allow embedding in iframe on same domain"""
    proxyClientFactoryClass = SatProxyClientFactory

    def getChild(self, path, request):
        return SatReverseProxyResource(
            self.host, self.port,
            self.path + b'/' + urlquote(path, safe=b"").encode('utf-8'),
            self.reactor
        )

    def render(self, request):
        # Forwarded and X-Forwarded-xxx headers can be set if we have behin an other proxy
        if ((not request.getHeader(C.H_FORWARDED)
             and not request.getHeader(C.H_X_FORWARDED_HOST))):
            forwarded_data = []
            addr = request.getClientAddress()
            if ((isinstance(addr, address.IPv4Address)
                 or isinstance(addr, address.IPv6Address))):
                request.requestHeaders.setRawHeaders(C.H_X_FORWARDED_FOR, [addr.host])
                forwarded_data.append(f"for={addr.host}")
            host = request.getHeader("host")
            if host is None:
                port = request.getHost().port
                hostname = request.getRequestHostname()
                host = hostname if port in (80, 443) else f"{hostname}:{port}"
            request.requestHeaders.setRawHeaders(C.H_X_FORWARDED_HOST, [host])
            forwarded_data.append(f"host={host}")
            proto = "https" if request.isSecure() else "http"
            request.requestHeaders.setRawHeaders(C.H_X_FORWARDED_PROTO, [proto])
            forwarded_data.append(f"proto={proto}")
            request.requestHeaders.setRawHeaders(
                C.H_FORWARDED, [";".join(forwarded_data)]
            )

        return super().render(request)
