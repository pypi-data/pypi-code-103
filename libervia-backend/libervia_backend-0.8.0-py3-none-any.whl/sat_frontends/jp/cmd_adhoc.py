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
from sat_frontends.jp import xmlui_manager

__commands__ = ["AdHoc"]

FLAG_LOOP = "LOOP"
MAGIC_BAREJID = "@PROFILE_BAREJID@"


class Remote(base.CommandBase):
    def __init__(self, host):
        super(Remote, self).__init__(
            host, "remote", use_verbose=True, help=_("remote control a software")
        )

    def add_parser_options(self):
        self.parser.add_argument("software", type=str, help=_("software name"))
        self.parser.add_argument(
            "-j",
            "--jids",
            nargs="*",
            default=[],
            help=_("jids allowed to use the command"),
        )
        self.parser.add_argument(
            "-g",
            "--groups",
            nargs="*",
            default=[],
            help=_("groups allowed to use the command"),
        )
        self.parser.add_argument(
            "--forbidden-groups",
            nargs="*",
            default=[],
            help=_("groups that are *NOT* allowed to use the command"),
        )
        self.parser.add_argument(
            "--forbidden-jids",
            nargs="*",
            default=[],
            help=_("jids that are *NOT* allowed to use the command"),
        )
        self.parser.add_argument(
            "-l", "--loop", action="store_true", help=_("loop on the commands")
        )

    async def start(self):
        name = self.args.software.lower()
        flags = []
        magics = {jid for jid in self.args.jids if jid.count("@") > 1}
        magics.add(MAGIC_BAREJID)
        jids = set(self.args.jids).difference(magics)
        if self.args.loop:
            flags.append(FLAG_LOOP)
        try:
            bus_name, methods = await self.host.bridge.adHocDBusAddAuto(
                name,
                list(jids),
                self.args.groups,
                magics,
                self.args.forbidden_jids,
                self.args.forbidden_groups,
                flags,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't create remote control: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if not bus_name:
                self.disp(_("No bus name found"), 1)
                self.host.quit(C.EXIT_NOT_FOUND)
            else:
                self.disp(_("Bus name found: [%s]" % bus_name), 1)
                for method in methods:
                    path, iface, command = method
                    self.disp(
                        _("Command found: (path:{path}, iface: {iface}) [{command}]")
                        .format(path=path, iface=iface, command=command),
                        1,
                    )
                self.host.quit()


class Run(base.CommandBase):
    """Run an Ad-Hoc command"""

    def __init__(self, host):
        super(Run, self).__init__(
            host, "run", use_verbose=True, help=_("run an Ad-Hoc command")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            default="",
            help=_("jid of the service (default: profile's server"),
        )
        self.parser.add_argument(
            "-S",
            "--submit",
            action="append_const",
            const=xmlui_manager.SUBMIT,
            dest="workflow",
            help=_("submit form/page"),
        )
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="workflow",
            metavar=("KEY", "VALUE"),
            help=_("field value"),
        )
        self.parser.add_argument(
            "node",
            nargs="?",
            default="",
            help=_("node of the command (default: list commands)"),
        )

    async def start(self):
        try:
            xmlui_raw = await self.host.bridge.adHocRun(
                self.args.jid,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get ad-hoc commands list: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            xmlui = xmlui_manager.create(self.host, xmlui_raw)
            workflow = self.args.workflow
            await xmlui.show(workflow)
            if not workflow:
                if xmlui.type == "form":
                    await xmlui.submitForm()
            self.host.quit()


class List(base.CommandBase):
    """List Ad-Hoc commands available on a service"""

    def __init__(self, host):
        super(List, self).__init__(
            host, "list", use_verbose=True, help=_("list Ad-Hoc commands of a service")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            default="",
            help=_("jid of the service (default: profile's server)"),
        )

    async def start(self):
        try:
            xmlui_raw = await self.host.bridge.adHocList(
                self.args.jid,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get ad-hoc commands list: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            xmlui = xmlui_manager.create(self.host, xmlui_raw)
            await xmlui.show(read_only=True)
            self.host.quit()


class AdHoc(base.CommandBase):
    subcommands = (Run, List, Remote)

    def __init__(self, host):
        super(AdHoc, self).__init__(
            host, "ad-hoc", use_profile=False, help=_("Ad-hoc commands")
        )
