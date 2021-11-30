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


import os
import os.path
import asyncio
from . import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat.tools import config
from sat.tools.common import data_format


__commands__ = ["Avatar"]
DISPLAY_CMD = ["xdg-open", "xv", "display", "gwenview", "showtell"]


class Get(base.CommandBase):
    def __init__(self, host):
        super(Get, self).__init__(
            host, "get", use_verbose=True, help=_("retrieve avatar of an entity")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "--no-cache", action="store_true", help=_("do no use cached values")
        )
        self.parser.add_argument(
            "-s", "--show", action="store_true", help=_("show avatar")
        )
        self.parser.add_argument("jid", nargs='?', default='', help=_("entity"))

    async def showImage(self, path):
        sat_conf = config.parseMainConf()
        cmd = config.getConfig(sat_conf, C.CONFIG_SECTION, "image_cmd")
        cmds = [cmd] + DISPLAY_CMD if cmd else DISPLAY_CMD
        for cmd in cmds:
            try:
                process = await asyncio.create_subprocess_exec(cmd, path)
                ret = await process.wait()
            except OSError:
                continue

            if ret in (0, 2):
                # we can get exit code 2 with display when stopping it with C-c
                break
        else:
            # didn't worked with commands, we try our luck with webbrowser
            # in some cases, webbrowser can actually open the associated display program.
            # Note that this may be possibly blocking, depending on the platform and
            # available browser
            import webbrowser

            webbrowser.open(path)

    async def start(self):
        try:
            avatar_data_raw = await self.host.bridge.avatarGet(
                self.args.jid,
                not self.args.no_cache,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't retrieve avatar: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        avatar_data = data_format.deserialise(avatar_data_raw, type_check=None)

        if not avatar_data:
            self.disp(_("No avatar found."), 1)
            self.host.quit(C.EXIT_NOT_FOUND)

        avatar_path = avatar_data['path']

        self.disp(avatar_path)
        if self.args.show:
            await self.showImage(avatar_path)

        self.host.quit()


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(
            host, "set", use_verbose=True,
            help=_("set avatar of the profile or an entity")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-j", "--jid", default='', help=_("entity whose avatar must be changed"))
        self.parser.add_argument(
            "image_path", type=str, help=_("path to the image to upload")
        )

    async def start(self):
        path = self.args.image_path
        if not os.path.exists(path):
            self.disp(_("file {path} doesn't exist!").format(path=repr(path)), error=True)
            self.host.quit(C.EXIT_BAD_ARG)
        path = os.path.abspath(path)
        try:
            await self.host.bridge.avatarSet(path, self.args.jid, self.profile)
        except Exception as e:
            self.disp(f"can't set avatar: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("avatar has been set"), 1)
            self.host.quit()


class Avatar(base.CommandBase):
    subcommands = (Get, Set)

    def __init__(self, host):
        super(Avatar, self).__init__(
            host, "avatar", use_profile=False, help=_("avatar uploading/retrieving")
        )
