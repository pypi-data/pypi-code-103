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


import os.path
from . import base
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import xmlui_manager
from sat_frontends.jp import common

__commands__ = ["MergeRequest"]


class Set(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_defaults={"service": _("auto"), "node": _("auto")},
            help=_("publish or update a merge request"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-i",
            "--item",
            default="",
            help=_("id or URL of the request to update, or nothing for a new one"),
        )
        self.parser.add_argument(
            "-r",
            "--repository",
            metavar="PATH",
            default=".",
            help=_("path of the repository (DEFAULT: current directory)"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("publish merge request without confirmation"),
        )
        self.parser.add_argument(
            "-l",
            "--label",
            dest="labels",
            action="append",
            help=_("labels to categorize your request"),
        )

    async def start(self):
        self.repository = os.path.expanduser(os.path.abspath(self.args.repository))
        await common.fill_well_known_uri(self, self.repository, "merge requests")
        if not self.args.force:
            message = _(
                "You are going to publish your changes to service "
                "[{service}], are you sure ?"
            ).format(service=self.args.service)
            await self.host.confirmOrQuit(
                message, _("merge request publication cancelled")
            )

        extra = {"update": True} if self.args.item else {}
        values = {}
        if self.args.labels is not None:
            values["labels"] = self.args.labels
        try:
            published_id = await self.host.bridge.mergeRequestSet(
                self.args.service,
                self.args.node,
                self.repository,
                "auto",
                values,
                "",
                self.args.item,
                data_format.serialise(extra),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't create merge requests: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        if published_id:
            self.disp(
                _("Merge request published at {published_id}").format(
                    published_id=published_id
                )
            )
        else:
            self.disp(_("Merge request published"))

        self.host.quit(C.EXIT_OK)


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS},
            pubsub_defaults={"service": _("auto"), "node": _("auto")},
            help=_("get a merge request"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        await common.fill_well_known_uri(self, os.getcwd(), "merge requests", meta_map={})
        extra = {}
        try:
            requests_data = data_format.deserialise(
                await self.host.bridge.mergeRequestsGet(
                    self.args.service,
                    self.args.node,
                    self.args.max,
                    self.args.items,
                    "",
                    extra,
                    self.profile,
                )
            )
        except Exception as e:
            self.disp(f"can't get merge request: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        if self.verbosity >= 1:
            whitelist = None
        else:
            whitelist = {"id", "title", "body"}
        for request_xmlui in requests_data["items"]:
            xmlui = xmlui_manager.create(self.host, request_xmlui, whitelist=whitelist)
            await xmlui.show(values_only=True)
            self.disp("")
        self.host.quit(C.EXIT_OK)


class Import(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "import",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM, C.ITEM},
            pubsub_defaults={"service": _("auto"), "node": _("auto")},
            help=_("import a merge request"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-r",
            "--repository",
            metavar="PATH",
            default=".",
            help=_("path of the repository (DEFAULT: current directory)"),
        )

    async def start(self):
        self.repository = os.path.expanduser(os.path.abspath(self.args.repository))
        await common.fill_well_known_uri(
            self, self.repository, "merge requests", meta_map={}
        )
        extra = {}
        try:
            await self.host.bridge.mergeRequestsImport(
                self.repository,
                self.args.item,
                self.args.service,
                self.args.node,
                extra,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't import merge request: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class MergeRequest(base.CommandBase):
    subcommands = (Set, Get, Import)

    def __init__(self, host):
        super(MergeRequest, self).__init__(
            host, "merge-request", use_profile=False, help=_("merge-request management")
        )
