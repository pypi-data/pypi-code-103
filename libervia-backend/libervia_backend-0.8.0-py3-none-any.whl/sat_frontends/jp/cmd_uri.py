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
from sat.tools.common import uri

__commands__ = ["Uri"]


class Parse(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "parse",
            use_profile=False,
            use_output=C.OUTPUT_DICT,
            help=_("parse URI"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "uri", help=_("XMPP URI to parse")
        )

    async def start(self):
        await self.output(uri.parseXMPPUri(self.args.uri))
        self.host.quit()


class Build(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "build", use_profile=False, help=_("build URI")
        )

    def add_parser_options(self):
        self.parser.add_argument("type", help=_("URI type"))
        self.parser.add_argument("path", help=_("URI path"))
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            metavar=("KEY", "VALUE"),
            help=_("URI fields"),
        )

    async def start(self):
        fields = dict(self.args.fields) if self.args.fields else {}
        self.disp(uri.buildXMPPUri(self.args.type, path=self.args.path, **fields))
        self.host.quit()


class Uri(base.CommandBase):
    subcommands = (Parse, Build)

    def __init__(self, host):
        super(Uri, self).__init__(
            host, "uri", use_profile=False, help=_("XMPP URI parsing/generation")
        )
