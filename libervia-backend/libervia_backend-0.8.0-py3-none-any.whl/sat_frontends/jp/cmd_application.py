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
from sat.tools.common import data_format
from sat_frontends.jp.constants import Const as C

__commands__ = ["Application"]


class List(base.CommandBase):
    """List available applications"""

    def __init__(self, host):
        super(List, self).__init__(
            host, "list", use_profile=False, use_output=C.OUTPUT_LIST,
            help=_("list available applications")
        )

    def add_parser_options(self):
        # FIXME: "extend" would be better here, but it's only available from Python 3.8+
        #   so we use "append" until minimum version of Python is raised.
        self.parser.add_argument(
            "-f",
            "--filter",
            dest="filters",
            action="append",
            choices=["available", "running"],
            help=_("show applications with this status"),
        )

    async def start(self):

        # FIXME: this is only needed because we can't use "extend" in
        #   add_parser_options, see note there
        if self.args.filters:
            self.args.filters = list(set(self.args.filters))
        else:
            self.args.filters = ['available']

        try:
            found_apps = await self.host.bridge.applicationsList(self.args.filters)
        except Exception as e:
            self.disp(f"can't get applications list: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(found_apps)
            self.host.quit()


class Start(base.CommandBase):
    """Start an application"""

    def __init__(self, host):
        super(Start, self).__init__(
            host, "start", use_profile=False, help=_("start an application")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "name",
            help=_("name of the application to start"),
        )

    async def start(self):
        try:
            await self.host.bridge.applicationStart(
                self.args.name,
                "",
            )
        except Exception as e:
            self.disp(f"can't start {self.args.name}: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class Stop(base.CommandBase):

    def __init__(self, host):
        super(Stop, self).__init__(
            host, "stop", use_profile=False, help=_("stop a running application")
        )

    def add_parser_options(self):
        id_group = self.parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument(
            "name",
            nargs="?",
            help=_("name of the application to stop"),
        )
        id_group.add_argument(
            "-i",
            "--id",
            help=_("identifier of the instance to stop"),
        )

    async def start(self):
        try:
            if self.args.name is not None:
                args = [self.args.name, "name"]
            else:
                args = [self.args.id, "instance"]
            await self.host.bridge.applicationStop(
                *args,
                "",
            )
        except Exception as e:
            if self.args.name is not None:
                self.disp(
                    f"can't stop application {self.args.name!r}: {e}", error=True)
            else:
                self.disp(
                    f"can't stop application instance with id {self.args.id!r}: {e}",
                    error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class Exposed(base.CommandBase):

    def __init__(self, host):
        super(Exposed, self).__init__(
            host, "exposed", use_profile=False, use_output=C.OUTPUT_DICT,
            help=_("show data exposed by a running application")
        )

    def add_parser_options(self):
        id_group = self.parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument(
            "name",
            nargs="?",
            help=_("name of the application to check"),
        )
        id_group.add_argument(
            "-i",
            "--id",
            help=_("identifier of the instance to check"),
        )

    async def start(self):
        try:
            if self.args.name is not None:
                args = [self.args.name, "name"]
            else:
                args = [self.args.id, "instance"]
            exposed_data_raw = await self.host.bridge.applicationExposedGet(
                *args,
                "",
            )
        except Exception as e:
            if self.args.name is not None:
                self.disp(
                    f"can't get values exposed from application {self.args.name!r}: {e}",
                    error=True)
            else:
                self.disp(
                    f"can't values exposed from  application instance with id {self.args.id!r}: {e}",
                    error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            exposed_data = data_format.deserialise(exposed_data_raw)
            await self.output(exposed_data)
            self.host.quit()


class Application(base.CommandBase):
    subcommands = (List, Start, Stop, Exposed)

    def __init__(self, host):
        super(Application, self).__init__(
            host, "application", use_profile=False, help=_("manage applications"),
            aliases=['app'],
        )
