#!/usr/bin/env python3


# jp: a SAT command line tool
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

import socket
import asyncio
import errno
from functools import partial
from sat_frontends.jp import base
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import xmlui_manager
import sys
from sat.core.i18n import _
from sat_frontends.tools import jid

__commands__ = ["Pipe"]

START_PORT = 9999


class PipeOut(base.CommandBase):
    def __init__(self, host):
        super(PipeOut, self).__init__(host, "out", help=_("send a pipe a stream"))

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", help=_("the destination jid")
        )

    async def start(self):
        """ Create named pipe, and send stdin to it """
        try:
            port = await self.host.bridge.streamOut(
                await self.host.get_full_jid(self.args.jid),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't start stream: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            # FIXME: we use temporarily blocking code here, as it simplify
            #        asyncio port: "loop.connect_read_pipe(lambda: reader_protocol,
            #        sys.stdin.buffer)" doesn't work properly when a file is piped in
            #        (we get a "ValueError: Pipe transport is for pipes/sockets only.")
            #        while it's working well for simple text sending.

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", int(port)))

            while True:
                buf = sys.stdin.buffer.read(4096)
                if not buf:
                    break
                try:
                    s.sendall(buf)
                except socket.error as e:
                    if e.errno == errno.EPIPE:
                        sys.stderr.write(f"e\n")
                        self.host.quit(1)
                    else:
                        raise e
            self.host.quit()


async def handle_stream_in(reader, writer, host):
    """Write all received data to stdout"""
    while True:
        data = await reader.read(4096)
        if not data:
            break
        sys.stdout.buffer.write(data)
        try:
            sys.stdout.flush()
        except IOError as e:
            sys.stderr.write(f"{e}\n")
            break
    host.quitFromSignal()


class PipeIn(base.CommandAnswering):
    def __init__(self, host):
        super(PipeIn, self).__init__(host, "in", help=_("receive a pipe stream"))
        self.action_callbacks = {"STREAM": self.onStreamAction}

    def add_parser_options(self):
        self.parser.add_argument(
            "jids",
            nargs="*",
            help=_('Jids accepted (none means "accept everything")'),
        )

    def getXmluiId(self, action_data):
        try:
            xml_ui = action_data["xmlui"]
        except KeyError:
            self.disp(_("Action has no XMLUI"), 1)
        else:
            ui = xmlui_manager.create(self.host, xml_ui)
            if not ui.submit_id:
                self.disp(_("Invalid XMLUI received"), error=True)
                self.quitFromSignal(C.EXIT_INTERNAL_ERROR)
            return ui.submit_id

    async def onStreamAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            self.host.quitFromSignal(C.EXIT_ERROR)
        try:
            from_jid = jid.JID(action_data["meta_from_jid"])
        except KeyError:
            self.disp(_("Ignoring action without from_jid data"), error=True)
            return

        if not self.bare_jids or from_jid.bare in self.bare_jids:
            host, port = "localhost", START_PORT
            while True:
                try:
                    server = await asyncio.start_server(
                        partial(handle_stream_in, host=self.host), host, port)
                except socket.error as e:
                    if e.errno == errno.EADDRINUSE:
                        port += 1
                    else:
                        raise e
                else:
                    break
            xmlui_data = {"answer": C.BOOL_TRUE, "port": str(port)}
            await self.host.bridge.launchAction(
                xmlui_id, xmlui_data, profile_key=profile)
            async with server:
                await server.serve_forever()
            self.host.quitFromSignal()

    async def start(self):
        self.bare_jids = [jid.JID(jid_).bare for jid_ in self.args.jids]
        await self.start_answering()


class Pipe(base.CommandBase):
    subcommands = (PipeOut, PipeIn)

    def __init__(self, host):
        super(Pipe, self).__init__(
            host, "pipe", use_profile=False, help=_("stream piping through XMPP")
        )
