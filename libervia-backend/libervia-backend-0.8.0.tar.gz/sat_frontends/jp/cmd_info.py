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
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import date_utils, data_format
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common

__commands__ = ["Info"]


class Disco(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(Disco, self).__init__(
            host,
            "disco",
            use_output="complex",
            extra_outputs=extra_outputs,
            help=_("service discovery"),
        )

    def add_parser_options(self):
        self.parser.add_argument("jid", help=_("entity to discover"))
        self.parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=("infos", "items", "both"),
            default="both",
            help=_("type of data to discover"),
        )
        self.parser.add_argument("-n", "--node", default="", help=_("node to use"))
        self.parser.add_argument(
            "-C",
            "--no-cache",
            dest="use_cache",
            action="store_false",
            help=_("ignore cache"),
        )

    def default_output(self, data):
        features = data.get("features", [])
        identities = data.get("identities", [])
        extensions = data.get("extensions", {})
        items = data.get("items", [])

        identities_table = common.Table(
            self.host,
            identities,
            headers=(_("category"), _("type"), _("name")),
            use_buffer=True,
        )

        extensions_tpl = []
        extensions_types = list(extensions.keys())
        extensions_types.sort()
        for type_ in extensions_types:
            fields = []
            for field in extensions[type_]:
                field_lines = []
                data, values = field
                data_keys = list(data.keys())
                data_keys.sort()
                for key in data_keys:
                    field_lines.append(
                        A.color("\t", C.A_SUBHEADER, key, A.RESET, ": ", data[key])
                    )
                if len(values) == 1:
                    field_lines.append(
                        A.color(
                            "\t",
                            C.A_SUBHEADER,
                            "value",
                            A.RESET,
                            ": ",
                            values[0] or (A.BOLD + "UNSET"),
                        )
                    )
                elif len(values) > 1:
                    field_lines.append(
                        A.color("\t", C.A_SUBHEADER, "values", A.RESET, ": ")
                    )

                    for value in values:
                        field_lines.append(A.color("\t  - ", A.BOLD, value))
                fields.append("\n".join(field_lines))
            extensions_tpl.append(
                "{type_}\n{fields}".format(type_=type_, fields="\n\n".join(fields))
            )

        items_table = common.Table(
            self.host, items, headers=(_("entity"), _("node"), _("name")), use_buffer=True
        )

        template = []
        if features:
            template.append(A.color(C.A_HEADER, _("Features")) + "\n\n{features}")
        if identities:
            template.append(A.color(C.A_HEADER, _("Identities")) + "\n\n{identities}")
        if extensions:
            template.append(A.color(C.A_HEADER, _("Extensions")) + "\n\n{extensions}")
        if items:
            template.append(A.color(C.A_HEADER, _("Items")) + "\n\n{items}")

        print(
            "\n\n".join(template).format(
                features="\n".join(features),
                identities=identities_table.display().string,
                extensions="\n".join(extensions_tpl),
                items=items_table.display().string,
            )
        )

    async def start(self):
        infos_requested = self.args.type in ("infos", "both")
        items_requested = self.args.type in ("items", "both")
        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]

        # infos
        if not infos_requested:
            infos = None
        else:
            try:
                infos = await self.host.bridge.discoInfos(
                    jid,
                    node=self.args.node,
                    use_cache=self.args.use_cache,
                    profile_key=self.host.profile,
                )
            except Exception as e:
                self.disp(_("error while doing discovery: {e}").format(e=e), error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

                # items
        if not items_requested:
            items = None
        else:
            try:
                items = await self.host.bridge.discoItems(
                    jid,
                    node=self.args.node,
                    use_cache=self.args.use_cache,
                    profile_key=self.host.profile,
                )
            except Exception as e:
                self.disp(_("error while doing discovery: {e}").format(e=e), error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

                # output
        data = {}

        if infos_requested:
            features, identities, extensions = infos
            features.sort()
            identities.sort(key=lambda identity: identity[2])
            data.update(
                {"features": features, "identities": identities, "extensions": extensions}
            )

        if items_requested:
            items.sort(key=lambda item: item[2])
            data["items"] = items

        await self.output(data)
        self.host.quit()


class Version(base.CommandBase):
    def __init__(self, host):
        super(Version, self).__init__(host, "version", help=_("software version"))

    def add_parser_options(self):
        self.parser.add_argument("jid", type=str, help=_("Entity to request"))

    async def start(self):
        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]
        try:
            data = await self.host.bridge.getSoftwareVersion(jid, self.host.profile)
        except Exception as e:
            self.disp(_("error while trying to get version: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            infos = []
            name, version, os = data
            if name:
                infos.append(_("Software name: {name}").format(name=name))
            if version:
                infos.append(_("Software version: {version}").format(version=version))
            if os:
                infos.append(_("Operating System: {os}").format(os=os))

            print("\n".join(infos))
            self.host.quit()


class Session(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(Session, self).__init__(
            host,
            "session",
            use_output="dict",
            extra_outputs=extra_outputs,
            help=_("running session"),
        )

    def add_parser_options(self):
        pass

    async def default_output(self, data):
        started = data["started"]
        data["started"] = "{short} (UTC, {relative})".format(
            short=date_utils.date_fmt(started),
            relative=date_utils.date_fmt(started, "relative"),
        )
        await self.host.output(C.OUTPUT_DICT, "simple", {}, data)

    async def start(self):
        try:
            data = await self.host.bridge.sessionInfosGet(self.host.profile)
        except Exception as e:
            self.disp(_("Error getting session infos: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(data)
            self.host.quit()


class Devices(base.CommandBase):
    def __init__(self, host):
        super(Devices, self).__init__(
            host, "devices", use_output=C.OUTPUT_LIST_DICT, help=_("devices of an entity")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=str, nargs="?", default="", help=_("Entity to request")
        )

    async def start(self):
        try:
            data = await self.host.bridge.devicesInfosGet(
                self.args.jid, self.host.profile
            )
        except Exception as e:
            self.disp(_("Error getting devices infos: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            data = data_format.deserialise(data, type_check=list)
            await self.output(data)
            self.host.quit()


class Info(base.CommandBase):
    subcommands = (Disco, Version, Session, Devices)

    def __init__(self, host):
        super(Info, self).__init__(
            host,
            "info",
            use_profile=False,
            help=_("Get various pieces of information on entities"),
        )
