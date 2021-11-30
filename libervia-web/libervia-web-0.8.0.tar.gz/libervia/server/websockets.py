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


import json
from twisted.internet import error
from autobahn.twisted import websocket
from autobahn.twisted import resource as resource
from autobahn.websocket import types
from sat.core import exceptions
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)

LIBERVIA_PROTOCOL = "libervia_page"


class WebsocketRequest(object):
    """Wrapper around autobahn's ConnectionRequest and Twisted's server.Request

    This is used to have a common interface in Libervia page with request object
    """

    def __init__(self, ws_protocol, connection_request, server_request):
        """
        @param connection_request: websocket request
        @param serveur_request: original request of the page
        """
        self.ws_protocol = ws_protocol
        self.ws_request = connection_request
        if self.isSecure():
            cookie_name = "TWISTED_SECURE_SESSION"
        else:
            cookie_name = "TWISTED_SESSION"
        cookie_value = server_request.getCookie(cookie_name.encode('utf-8'))
        try:
            raw_cookies = ws_protocol.http_headers['cookie']
        except KeyError:
            raise ValueError("missing expected cookie header")
        self.cookies = {k:v for k,v in (c.split('=') for c in raw_cookies.split(';'))}
        if self.cookies[cookie_name] != cookie_value.decode('utf-8'):
            raise exceptions.PermissionError(
                "Bad cookie value, this should never happen.\n"
                "headers: {headers}".format(headers=ws_protocol.http_headers))

        self.template_data = server_request.template_data
        self.data = server_request.data
        self.session = server_request.getSession()
        self._signals_registered = server_request._signals_registered
        self._signals_cache = server_request._signals_cache
        # signal id is needed to link original request with signal handler
        self.signal_id = server_request._signal_id

    def isSecure(self):
        return self.ws_protocol.factory.isSecure

    def getSession(self, sessionInterface=None):
        try:
            self.session.touch()
        except (error.AlreadyCalled, error.AlreadyCancelled):
            # Session has already expired.
            self.session = None

        if sessionInterface:
            return self.session.getComponent(sessionInterface)

        return self.session

    def sendData(self, type_, **data):
        assert "type" not in data
        data["type"] = type_
        self.ws_protocol.sendMessage(json.dumps(data, ensure_ascii=False).encode("utf8"))


class LiberviaPageWSProtocol(websocket.WebSocketServerProtocol):
    host = None
    tokens_map = {}

    def onConnect(self, request):
        prefix = LIBERVIA_PROTOCOL + "_"
        for protocol in request.protocols:
            if protocol.startswith(prefix):
                token = protocol[len(prefix) :].strip()
                if token:
                    break
        else:
            raise types.ConnectionDeny(
                types.ConnectionDeny.NOT_IMPLEMENTED, "Can't use this subprotocol"
            )

        if token not in self.tokens_map:
            log.warning(_("Can't activate page socket: unknown token"))
            raise types.ConnectionDeny(
                types.ConnectionDeny.FORBIDDEN, "Bad token, please reload page"
            )
        self.token = token
        token_map = self.tokens_map.pop(token)
        self.page = token_map["page"]
        self.request = WebsocketRequest(self, request, token_map["request"])
        return protocol

    def onOpen(self):
        log.debug(
            _(
                "Websocket opened for {page} (token: {token})".format(
                    page=self.page, token=self.token
                )
            )
        )
        self.page.onSocketOpen(self.request)

    def onMessage(self, payload, isBinary):
        try:
            data_json = json.loads(payload.decode("utf8"))
        except ValueError as e:
            log.warning(
                _("Not valid JSON, ignoring data: {msg}\n{data}").format(
                    msg=e, data=payload
                )
            )
            return
        #  we request page first, to raise an AttributeError
        # if it is not set (which should never happen)
        page = self.page
        try:
            cb = page.on_data
        except AttributeError:
            log.warning(
                _(
                    'No "on_data" method set on dynamic page, ignoring data:\n{data}'
                ).format(data=data_json)
            )
        else:
            cb(page, self.request, data_json)

    def onClose(self, wasClean, code, reason):
        try:
            page = self.page
        except AttributeError:
            log.debug(
                "page is not available, the socket was probably not opened cleanly.\n"
                "reason: {reason}".format(reason=reason))
            return
        page.onSocketClose(self.request)

        log.debug(
            _(
                "Websocket closed for {page} (token: {token}). {reason}".format(
                    page=self.page,
                    token=self.token,
                    reason=""
                    if wasClean
                    else _("Reason: {reason}").format(reason=reason),
                )
            )
        )

    @classmethod
    def getBaseURL(cls, host, secure):
        return "ws{sec}://localhost:{port}".format(
            sec="s" if secure else "",
            port=cls.host.options["port_https" if secure else "port"],
        )

    @classmethod
    def getResource(cls, host, secure):
        if cls.host is None:
            cls.host = host
        factory = websocket.WebSocketServerFactory(cls.getBaseURL(host, secure))
        factory.protocol = cls
        return resource.WebSocketResource(factory)

    @classmethod
    def registerToken(cls, token, page, request):
        if token in cls.tokens_map:
            raise exceptions.ConflictError(_("This token is already registered"))
        cls.tokens_map[token] = {"page": page, "request": request}
