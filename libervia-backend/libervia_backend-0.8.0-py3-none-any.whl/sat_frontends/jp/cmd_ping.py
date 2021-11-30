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

from . import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C

__commands__ = ["Ping"]


class Ping(base.CommandBase):
    def __init__(self, host):
        super(Ping, self).__init__(host, "ping", help=_("ping XMPP entity"))

    def add_parser_options(self):
        self.parser.add_argument("jid", help=_("jid to ping"))
        self.parser.add_argument(
            "-d", "--delay-only", action="store_true", help=_("output delay only (in s)")
        )

    async def start(self):
        try:
            pong_time = await self.host.bridge.ping(self.args.jid, self.profile)
        except Exception as e:
            self.disp(msg=_("can't do the ping: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            msg = pong_time if self.args.delay_only else f"PONG ({pong_time} s)"
            self.disp(msg)
            self.host.quit()
