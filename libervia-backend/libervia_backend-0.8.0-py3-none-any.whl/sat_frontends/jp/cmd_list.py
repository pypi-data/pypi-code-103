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


import json
import os
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.jp import common
from sat_frontends.jp.constants import Const as C
from . import base

__commands__ = ["List"]

FIELDS_MAP = "mapping"


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
            use_output=C.OUTPUT_LIST_XMLUI,
            help=_("get lists"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        await common.fill_well_known_uri(self, os.getcwd(), "tickets", meta_map={})
        try:
            lists_data = data_format.deserialise(
                await self.host.bridge.listGet(
                    self.args.service,
                    self.args.node,
                    self.args.max,
                    self.args.items,
                    "",
                    self.getPubsubExtra(),
                    self.profile,
                ),
                type_check=list,
            )
        except Exception as e:
            self.disp(f"can't get lists: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(lists_data[0])
            self.host.quit(C.EXIT_OK)


class Set(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_defaults={"service": _("auto"), "node": _("auto")},
            help=_("set a list item"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs="+",
            dest="fields",
            required=True,
            metavar=("NAME", "VALUES"),
            help=_("field(s) to set (required)"),
        )
        self.parser.add_argument(
            "-U",
            "--update",
            choices=("auto", "true", "false"),
            default="auto",
            help=_("update existing item instead of replacing it (DEFAULT: auto)"),
        )
        self.parser.add_argument(
            "item",
            nargs="?",
            default="",
            help=_("id, URL of the item to update, or nothing for new item"),
        )

    async def start(self):
        await common.fill_well_known_uri(self, os.getcwd(), "tickets", meta_map={})
        if self.args.update == "auto":
            # we update if we have a item id specified
            update = bool(self.args.item)
        else:
            update = C.bool(self.args.update)

        values = {}

        for field_data in self.args.fields:
            values.setdefault(field_data[0], []).extend(field_data[1:])

        extra = {"update": update}

        try:
            item_id = await self.host.bridge.listSet(
                self.args.service,
                self.args.node,
                values,
                "",
                self.args.item,
                data_format.serialise(extra),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set list item: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(f"item {str(item_id or self.args.item)!r} set successfully")
            self.host.quit(C.EXIT_OK)


class Delete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_defaults={"service": _("auto"), "node": _("auto")},
            help=_("delete a list item"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f", "--force", action="store_true", help=_("delete without confirmation")
        )
        self.parser.add_argument(
            "-N", "--notify", action="store_true", help=_("notify deletion")
        )
        self.parser.add_argument(
            "item",
            help=_("id of the item to delete"),
        )

    async def start(self):
        await common.fill_well_known_uri(self, os.getcwd(), "tickets", meta_map={})
        if not self.args.item:
            self.parser.error(_("You need to specify a list item to delete"))
        if not self.args.force:
            message = _("Are you sure to delete list item {item_id} ?").format(
                item_id=self.args.item
            )
            await self.host.confirmOrQuit(message, _("item deletion cancelled"))
        try:
            await self.host.bridge.listDeleteItem(
                self.args.service,
                self.args.node,
                self.args.item,
                self.args.notify,
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't delete item: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("item {item} has been deleted").format(item=self.args.item))
            self.host.quit(C.EXIT_OK)


class Import(base.CommandBase):
    # TODO: factorize with blog/import

    def __init__(self, host):
        super(Import, self).__init__(
            host,
            "import",
            use_progress=True,
            use_verbose=True,
            help=_("import tickets from external software/dataset"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "importer",
            nargs="?",
            help=_("importer name, nothing to display importers list"),
        )
        self.parser.add_argument(
            "-o",
            "--option",
            action="append",
            nargs=2,
            default=[],
            metavar=("NAME", "VALUE"),
            help=_("importer specific options (see importer description)"),
        )
        self.parser.add_argument(
            "-m",
            "--map",
            action="append",
            nargs=2,
            default=[],
            metavar=("IMPORTED_FIELD", "DEST_FIELD"),
            help=_(
                "specified field in import data will be put in dest field (default: use "
                "same field name, or ignore if it doesn't exist)"
            ),
        )
        self.parser.add_argument(
            "-s",
            "--service",
            default="",
            metavar="PUBSUB_SERVICE",
            help=_("PubSub service where the items must be uploaded (default: server)"),
        )
        self.parser.add_argument(
            "-n",
            "--node",
            default="",
            metavar="PUBSUB_NODE",
            help=_(
                "PubSub node where the items must be uploaded (default: tickets' "
                "defaults)"
            ),
        )
        self.parser.add_argument(
            "location",
            nargs="?",
            help=_(
                "importer data location (see importer description), nothing to show "
                "importer description"
            ),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("Tickets upload started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("Tickets uploaded successfully"), 2)

    async def onProgressError(self, error_msg):
        self.disp(
            _("Error while uploading tickets: {error_msg}").format(error_msg=error_msg),
            error=True,
        )

    async def start(self):
        if self.args.location is None:
            # no location, the list of importer or description is requested
            for name in ("option", "service", "node"):
                if getattr(self.args, name):
                    self.parser.error(
                        _(
                            "{name} argument can't be used without location argument"
                        ).format(name=name)
                    )
            if self.args.importer is None:
                self.disp(
                    "\n".join(
                        [
                            f"{name}: {desc}"
                            for name, desc in await self.host.bridge.ticketsImportList()
                        ]
                    )
                )
            else:
                try:
                    short_desc, long_desc = await self.host.bridge.ticketsImportDesc(
                        self.args.importer
                    )
                except Exception as e:
                    self.disp(f"can't get importer description: {e}", error=True)
                    self.host.quit(C.EXIT_BRIDGE_ERRBACK)
                else:
                    self.disp(f"{name}: {short_desc}\n\n{long_desc}")
            self.host.quit()
        else:
            # we have a location, an import is requested

            if self.args.progress:
                # we use a custom progress bar template as we want a counter
                self.pbar_template = [
                    _("Progress: "),
                    ["Percentage"],
                    " ",
                    ["Bar"],
                    " ",
                    ["Counter"],
                    " ",
                    ["ETA"],
                ]

            options = {key: value for key, value in self.args.option}
            fields_map = dict(self.args.map)
            if fields_map:
                if FIELDS_MAP in options:
                    self.parser.error(
                        _(
                            "fields_map must be specified either preencoded in --option or "
                            "using --map, but not both at the same time"
                        )
                    )
                options[FIELDS_MAP] = json.dumps(fields_map)

            try:
                progress_id = await self.host.bridge.ticketsImport(
                    self.args.importer,
                    self.args.location,
                    options,
                    self.args.service,
                    self.args.node,
                    self.profile,
                )
            except Exception as e:
                self.disp(
                    _("Error while trying to import tickets: {e}").format(e=e),
                    error=True,
                )
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
            else:
                await self.set_progress_id(progress_id)


class List(base.CommandBase):
    subcommands = (Get, Set, Delete, Import)

    def __init__(self, host):
        super(List, self).__init__(
            host, "list", use_profile=False, help=_("pubsub lists handling")
        )
