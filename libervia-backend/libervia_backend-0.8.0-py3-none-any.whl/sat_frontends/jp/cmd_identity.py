#!/usr/bin/env python3


# jp: a SàT command line tool
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
from sat.tools.common import data_format

__commands__ = ["Identity"]


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_verbose=True,
            help=_("get identity data"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "--no-cache", action="store_true", help=_("do no use cached values")
        )
        self.parser.add_argument(
            "jid", help=_("entity to check")
        )

    async def start(self):
        jid_ = (await self.host.check_jids([self.args.jid]))[0]
        try:
            data = await self.host.bridge.identityGet(
                jid_,
                [],
                not self.args.no_cache,
                self.profile
            )
        except Exception as e:
            self.disp(f"can't get identity data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            data = data_format.deserialise(data)
            await self.output(data)
            self.host.quit()


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(host, "set", help=_("update identity data"))

    def add_parser_options(self):
        self.parser.add_argument(
            "-n",
            "--nickname",
            action="append",
            dest="nicknames",
            required=True,
            help=_("nicknames of the entity"),
        )

    async def start(self):
        id_data = {
            "nicknames": self.args.nicknames,
        }
        try:
            self.host.bridge.identitySet(
                data_format.serialise(id_data),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set identity data: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class Identity(base.CommandBase):
    subcommands = (Get, Set)

    def __init__(self, host):
        super(Identity, self).__init__(
            host, "identity", use_profile=False, help=_("identity management")
        )
