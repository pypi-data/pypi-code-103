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
from sat_frontends.jp import common
from sat.tools.common.ansi import ANSI as A
import codecs
import json

__commands__ = ["Forums"]

FORUMS_TMP_DIR = "forums"


class Edit(base.CommandBase, common.BaseEdit):
    use_items = False

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            use_draft=True,
            use_verbose=True,
            help=_("edit forums"),
        )
        common.BaseEdit.__init__(self, self.host, FORUMS_TMP_DIR)

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            default="",
            help=_("forum key (DEFAULT: default forums)"),
        )

    def getTmpSuff(self):
        """return suffix used for content file"""
        return "json"

    async def publish(self, forums_raw):
        try:
            await self.host.bridge.forumsSet(
                forums_raw,
                self.args.service,
                self.args.node,
                self.args.key,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set forums: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("forums have been edited"), 1)
            self.host.quit()

    async def start(self):
        try:
            forums_json = await self.host.bridge.forumsGet(
                self.args.service,
                self.args.node,
                self.args.key,
                self.profile,
            )
        except Exception as e:
            if e.classname == "NotFound":
                forums_json = ""
            else:
                self.disp(f"can't get node configuration: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        content_file_obj, content_file_path = self.getTmpFile()
        forums_json = forums_json.strip()
        if forums_json:
            # we loads and dumps to have pretty printed json
            forums = json.loads(forums_json)
            # cf. https://stackoverflow.com/a/18337754
            f = codecs.getwriter("utf-8")(content_file_obj)
            json.dump(forums, f, ensure_ascii=False, indent=4)
            content_file_obj.seek(0)
        await self.runEditor("forums_editor_args", content_file_path, content_file_obj)


class Get(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            use_pubsub=True,
            use_verbose=True,
            help=_("get forums structure"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            default="",
            help=_("forum key (DEFAULT: default forums)"),
        )

    def default_output(self, forums, level=0):
        for forum in forums:
            keys = list(forum.keys())
            keys.sort()
            try:
                keys.remove("title")
            except ValueError:
                pass
            else:
                keys.insert(0, "title")
            try:
                keys.remove("sub-forums")
            except ValueError:
                pass
            else:
                keys.append("sub-forums")

            for key in keys:
                value = forum[key]
                if key == "sub-forums":
                    self.default_output(value, level + 1)
                else:
                    if self.host.verbosity < 1 and key != "title":
                        continue
                    head_color = C.A_LEVEL_COLORS[level % len(C.A_LEVEL_COLORS)]
                    self.disp(
                        A.color(level * 4 * " ", head_color, key, A.RESET, ": ", value)
                    )

    async def start(self):
        try:
            forums_raw = await self.host.bridge.forumsGet(
                self.args.service,
                self.args.node,
                self.args.key,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get forums: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if not forums_raw:
                self.disp(_("no schema found"), 1)
                self.host.quit(1)
            forums = json.loads(forums_raw)
            await self.output(forums)
            self.host.quit()


class Forums(base.CommandBase):
    subcommands = (Get, Edit)

    def __init__(self, host):
        super(Forums, self).__init__(
            host, "forums", use_profile=False, help=_("Forums structure edition")
        )
