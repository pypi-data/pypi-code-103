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

__commands__ = ["Bookmarks"]

STORAGE_LOCATIONS = ("local", "private", "pubsub")
TYPES = ("muc", "url")


class BookmarksCommon(base.CommandBase):
    """Class used to group common options of bookmarks subcommands"""

    def add_parser_options(self, location_default="all"):
        self.parser.add_argument(
            "-l",
            "--location",
            type=str,
            choices=(location_default,) + STORAGE_LOCATIONS,
            default=location_default,
            help=_("storage location (default: %(default)s)"),
        )
        self.parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=TYPES,
            default=TYPES[0],
            help=_("bookmarks type (default: %(default)s)"),
        )


class BookmarksList(BookmarksCommon):
    def __init__(self, host):
        super(BookmarksList, self).__init__(host, "list", help=_("list bookmarks"))

    async def start(self):
        try:
            data = await self.host.bridge.bookmarksList(
                self.args.type, self.args.location, self.host.profile
            )
        except Exception as e:
            self.disp(f"can't get bookmarks list: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        mess = []
        for location in STORAGE_LOCATIONS:
            if not data[location]:
                continue
            loc_mess = []
            loc_mess.append(f"{location}:")
            book_mess = []
            for book_link, book_data in list(data[location].items()):
                name = book_data.get("name")
                autojoin = book_data.get("autojoin", "false") == "true"
                nick = book_data.get("nick")
                book_mess.append(
                    "\t%s[%s%s]%s"
                    % (
                        (name + " ") if name else "",
                        book_link,
                        " (%s)" % nick if nick else "",
                        " (*)" if autojoin else "",
                    )
                )
            loc_mess.append("\n".join(book_mess))
            mess.append("\n".join(loc_mess))

        print("\n\n".join(mess))
        self.host.quit()


class BookmarksRemove(BookmarksCommon):
    def __init__(self, host):
        super(BookmarksRemove, self).__init__(host, "remove", help=_("remove a bookmark"))

    def add_parser_options(self):
        super(BookmarksRemove, self).add_parser_options()
        self.parser.add_argument(
            "bookmark", help=_("jid (for muc bookmark) or url of to remove")
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("delete bookmark without confirmation"),
        )

    async def start(self):
        if not self.args.force:
            await self.host.confirmOrQuit(_("Are you sure to delete this bookmark?"))

        try:
            await self.host.bridge.bookmarksRemove(
                self.args.type, self.args.bookmark, self.args.location, self.host.profile
            )
        except Exception as e:
            self.disp(_("can't delete bookmark: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("bookmark deleted"))
            self.host.quit()


class BookmarksAdd(BookmarksCommon):
    def __init__(self, host):
        super(BookmarksAdd, self).__init__(host, "add", help=_("add a bookmark"))

    def add_parser_options(self):
        super(BookmarksAdd, self).add_parser_options(location_default="auto")
        self.parser.add_argument(
            "bookmark", help=_("jid (for muc bookmark) or url of to remove")
        )
        self.parser.add_argument("-n", "--name", help=_("bookmark name"))
        muc_group = self.parser.add_argument_group(_("MUC specific options"))
        muc_group.add_argument("-N", "--nick", help=_("nickname"))
        muc_group.add_argument(
            "-a",
            "--autojoin",
            action="store_true",
            help=_("join room on profile connection"),
        )

    async def start(self):
        if self.args.type == "url" and (self.args.autojoin or self.args.nick is not None):
            self.parser.error(_("You can't use --autojoin or --nick with --type url"))
        data = {}
        if self.args.autojoin:
            data["autojoin"] = "true"
        if self.args.nick is not None:
            data["nick"] = self.args.nick
        if self.args.name is not None:
            data["name"] = self.args.name
        try:
            await self.host.bridge.bookmarksAdd(
                self.args.type,
                self.args.bookmark,
                data,
                self.args.location,
                self.host.profile,
            )
        except Exception as e:
            self.disp(f"can't add bookmark: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("bookmark successfully added"))
            self.host.quit()


class Bookmarks(base.CommandBase):
    subcommands = (BookmarksList, BookmarksRemove, BookmarksAdd)

    def __init__(self, host):
        super(Bookmarks, self).__init__(
            host, "bookmarks", use_profile=False, help=_("manage bookmarks")
        )
