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
import sys
import os.path
import os
import time
import tempfile
import subprocess
import asyncio
from asyncio.subprocess import DEVNULL
from pathlib import Path
from . import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import uri
from sat.tools import config
from configparser import NoSectionError, NoOptionError
from sat.tools.common import data_format

__commands__ = ["Blog"]

SYNTAX_XHTML = "xhtml"
# extensions to use with known syntaxes
SYNTAX_EXT = {
    # FIXME: default syntax doesn't sounds needed, there should always be a syntax set
    #        by the plugin.
    "": "txt",  # used when the syntax is not found
    SYNTAX_XHTML: "xhtml",
    "markdown": "md",
}


CONF_SYNTAX_EXT = "syntax_ext_dict"
BLOG_TMP_DIR = "blog"
# key to remove from metadata tmp file if they exist
KEY_TO_REMOVE_METADATA = (
    "id",
    "content",
    "content_xhtml",
    "comments_node",
    "comments_service",
    "updated",
)

URL_REDIRECT_PREFIX = "url_redirect_"
AIONOTIFY_INSTALL = '"pip install aionotify"'
MB_KEYS = (
    "id",
    "url",
    "atom_id",
    "updated",
    "published",
    "language",
    "comments",  # this key is used for all comments* keys
    "tags",  # this key is used for all tag* keys
    "author",
    "author_jid",
    "author_email",
    "author_jid_verified",
    "content",
    "content_xhtml",
    "title",
    "title_xhtml",
)
OUTPUT_OPT_NO_HEADER = "no-header"


async def guessSyntaxFromPath(host, sat_conf, path):
    """Return syntax guessed according to filename extension

    @param sat_conf(ConfigParser.ConfigParser): instance opened on sat configuration
    @param path(str): path to the content file
    @return(unicode): syntax to use
    """
    # we first try to guess syntax with extension
    ext = os.path.splitext(path)[1][1:]  # we get extension without the '.'
    if ext:
        for k, v in SYNTAX_EXT.items():
            if k and ext == v:
                return k

                # if not found, we use current syntax
    return await host.bridge.getParamA("Syntax", "Composition", "value", host.profile)


class BlogPublishCommon(object):
    """handle common option for publising commands (Set and Edit)"""

    async def get_current_syntax(self):
        """Retrieve current_syntax

        Use default syntax if --syntax has not been used, else check given syntax.
        Will set self.default_syntax_used to True if default syntax has been used
        """
        if self.args.syntax is None:
            self.default_syntax_used = True
            return await self.host.bridge.getParamA(
                "Syntax", "Composition", "value", self.profile
            )
        else:
            self.default_syntax_used = False
            try:
                syntax = await self.host.bridge.syntaxGet(self.args.syntax)
                self.current_syntax = self.args.syntax = syntax
            except Exception as e:
                if e.classname == "NotFound":
                    self.parser.error(
                        _("unknown syntax requested ({syntax})").format(
                            syntax=self.args.syntax
                        )
                    )
                else:
                    raise e
        return self.args.syntax

    def add_parser_options(self):
        self.parser.add_argument("-T", "--title", help=_("title of the item"))
        self.parser.add_argument(
            "-t",
            "--tag",
            action="append",
            help=_("tag (category) of your item"),
        )
        self.parser.add_argument(
            "-l",
            "--language",
            help=_("language of the item (ISO 639 code)"),
        )

        comments_group = self.parser.add_mutually_exclusive_group()
        comments_group.add_argument(
            "-C",
            "--comments",
            action="store_const",
            const=True,
            dest="comments",
            help=_(
                "enable comments (default: comments not enabled except if they "
                "already exist)"
            ),
        )
        comments_group.add_argument(
            "--no-comments",
            action="store_const",
            const=False,
            dest="comments",
            help=_("disable comments (will remove comments node if it exist)"),
        )

        self.parser.add_argument(
            "-S",
            "--syntax",
            help=_("syntax to use (default: get profile's default syntax)"),
        )

    async def setMbDataContent(self, content, mb_data):
        if self.default_syntax_used:
            # default syntax has been used
            mb_data["content_rich"] = content
        elif self.current_syntax == SYNTAX_XHTML:
            mb_data["content_xhtml"] = content
        else:
            mb_data["content_xhtml"] = await self.host.bridge.syntaxConvert(
                content, self.current_syntax, SYNTAX_XHTML, False, self.profile
            )

    def setMbDataFromArgs(self, mb_data):
        """set microblog metadata according to command line options

        if metadata already exist, it will be overwritten
        """
        if self.args.comments is not None:
            mb_data["allow_comments"] = self.args.comments
        if self.args.tag:
            mb_data["tags"] = self.args.tag
        if self.args.title is not None:
            mb_data["title"] = self.args.title
        if self.args.language is not None:
            mb_data["language"] = self.args.language


class Set(base.CommandBase, BlogPublishCommon):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            help=_("publish a new blog item or update an existing one"),
        )
        BlogPublishCommon.__init__(self)

    def add_parser_options(self):
        BlogPublishCommon.add_parser_options(self)

    async def start(self):
        self.current_syntax = await self.get_current_syntax()
        self.pubsub_item = self.args.item
        mb_data = {}
        self.setMbDataFromArgs(mb_data)
        if self.pubsub_item:
            mb_data["id"] = self.pubsub_item
        content = sys.stdin.read()
        await self.setMbDataContent(content, mb_data)

        try:
            await self.host.bridge.mbSend(
                self.args.service,
                self.args.node,
                data_format.serialise(mb_data),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't send item: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp("Item published")
            self.host.quit(C.EXIT_OK)


class Get(base.CommandBase):
    TEMPLATE = "blog/articles.html"

    def __init__(self, host):
        extra_outputs = {"default": self.default_output, "fancy": self.fancy_output}
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS},
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            help=_("get blog item(s)"),
        )

    def add_parser_options(self):
        #  TODO: a key(s) argument to select keys to display
        self.parser.add_argument(
            "-k",
            "--key",
            action="append",
            dest="keys",
            help=_("microblog data key(s) to display (default: depend of verbosity)"),
        )
        # TODO: add MAM filters

    def template_data_mapping(self, data):
        items, blog_items = data
        blog_items["items"] = items
        return {"blog_items": blog_items}

    def format_comments(self, item, keys):
        lines = []
        for data in item.get("comments", []):
            lines.append(data["uri"])
            for k in ("node", "service"):
                if OUTPUT_OPT_NO_HEADER in self.args.output_opts:
                    header = ""
                else:
                    header = f"{C.A_HEADER}comments_{k}: {A.RESET}"
                lines.append(header + data[k])
        return "\n".join(lines)

    def format_tags(self, item, keys):
        tags = item.pop("tags", [])
        return ", ".join(tags)

    def format_updated(self, item, keys):
        return self.format_time(item["updated"])

    def format_published(self, item, keys):
        return self.format_time(item["published"])

    def format_url(self, item, keys):
        return uri.buildXMPPUri(
            "pubsub",
            subtype="microblog",
            path=self.metadata["service"],
            node=self.metadata["node"],
            item=item["id"],
        )

    def get_keys(self):
        """return keys to display according to verbosity or explicit key request"""
        verbosity = self.args.verbose
        if self.args.keys:
            if not set(MB_KEYS).issuperset(self.args.keys):
                self.disp(
                    "following keys are invalid: {invalid}.\n"
                    "Valid keys are: {valid}.".format(
                        invalid=", ".join(set(self.args.keys).difference(MB_KEYS)),
                        valid=", ".join(sorted(MB_KEYS)),
                    ),
                    error=True,
                )
                self.host.quit(C.EXIT_BAD_ARG)
            return self.args.keys
        else:
            if verbosity == 0:
                return ("title", "content")
            elif verbosity == 1:
                return (
                    "title",
                    "tags",
                    "author",
                    "author_jid",
                    "author_email",
                    "author_jid_verified",
                    "published",
                    "updated",
                    "content",
                )
            else:
                return MB_KEYS

    def default_output(self, data):
        """simple key/value output"""
        items, self.metadata = data
        keys = self.get_keys()

        #  k_cb use format_[key] methods for complex formattings
        k_cb = {}
        for k in keys:
            try:
                callback = getattr(self, "format_" + k)
            except AttributeError:
                pass
            else:
                k_cb[k] = callback
        for idx, item in enumerate(items):
            for k in keys:
                if k not in item and k not in k_cb:
                    continue
                if OUTPUT_OPT_NO_HEADER in self.args.output_opts:
                    header = ""
                else:
                    header = "{k_fmt}{key}:{k_fmt_e} {sep}".format(
                        k_fmt=C.A_HEADER,
                        key=k,
                        k_fmt_e=A.RESET,
                        sep="\n" if "content" in k else "",
                    )
                value = k_cb[k](item, keys) if k in k_cb else item[k]
                if isinstance(value, bool):
                    value = str(value).lower()
                self.disp(header + value)
                # we want a separation line after each item but the last one
            if idx < len(items) - 1:
                print("")

    def format_time(self, timestamp):
        """return formatted date for timestamp

        @param timestamp(str,int,float): unix timestamp
        @return (unicode): formatted date
        """
        fmt = "%d/%m/%Y %H:%M:%S"
        return time.strftime(fmt, time.localtime(float(timestamp)))

    def fancy_output(self, data):
        """display blog is a nice to read way

        this output doesn't use keys filter
        """
        # thanks to http://stackoverflow.com/a/943921
        rows, columns = list(map(int, os.popen("stty size", "r").read().split()))
        items, metadata = data
        verbosity = self.args.verbose
        sep = A.color(A.FG_BLUE, columns * "▬")
        if items:
            print(("\n" + sep + "\n"))

        for idx, item in enumerate(items):
            title = item.get("title")
            if verbosity > 0:
                author = item["author"]
                published, updated = item["published"], item.get("updated")
            else:
                author = published = updated = None
            if verbosity > 1:
                tags = item.pop("tags", [])
            else:
                tags = None
            content = item.get("content")

            if title:
                print((A.color(A.BOLD, A.FG_CYAN, item["title"])))
            meta = []
            if author:
                meta.append(A.color(A.FG_YELLOW, author))
            if published:
                meta.append(A.color(A.FG_YELLOW, "on ", self.format_time(published)))
            if updated != published:
                meta.append(
                    A.color(A.FG_YELLOW, "(updated on ", self.format_time(updated), ")")
                )
            print((" ".join(meta)))
            if tags:
                print((A.color(A.FG_MAGENTA, ", ".join(tags))))
            if (title or tags) and content:
                print("")
            if content:
                self.disp(content)

            print(("\n" + sep + "\n"))

    async def start(self):
        try:
            mb_data = data_format.deserialise(
                await self.host.bridge.mbGet(
                    self.args.service,
                    self.args.node,
                    self.args.max,
                    self.args.items,
                    self.getPubsubExtra(),
                    self.profile,
                )
            )
        except Exception as e:
            self.disp(f"can't get blog items: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            items = mb_data.pop("items")
            await self.output((items, mb_data))
            self.host.quit(C.EXIT_OK)


class Edit(base.CommandBase, BlogPublishCommon, common.BaseEdit):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            use_draft=True,
            use_verbose=True,
            help=_("edit an existing or new blog post"),
        )
        BlogPublishCommon.__init__(self)
        common.BaseEdit.__init__(self, self.host, BLOG_TMP_DIR, use_metadata=True)

    def add_parser_options(self):
        BlogPublishCommon.add_parser_options(self)
        self.parser.add_argument(
            "-P",
            "--preview",
            action="store_true",
            help=_("launch a blog preview in parallel"),
        )
        self.parser.add_argument(
            "--no-publish",
            action="store_true",
            help=_('add "publish: False" to metadata'),
        )

    def buildMetadataFile(self, content_file_path, mb_data=None):
        """Build a metadata file using json

        The file is named after content_file_path, with extension replaced by
        _metadata.json
        @param content_file_path(str): path to the temporary file which will contain the
            body
        @param mb_data(dict, None): microblog metadata (for existing items)
        @return (tuple[dict, Path]): merged metadata put originaly in metadata file
            and path to temporary metadata file
        """
        # we first construct metadata from edited item ones and CLI argumments
        # or re-use the existing one if it exists
        meta_file_path = content_file_path.with_name(
            content_file_path.stem + common.METADATA_SUFF
        )
        if meta_file_path.exists():
            self.disp("Metadata file already exists, we re-use it")
            try:
                with meta_file_path.open("rb") as f:
                    mb_data = json.load(f)
            except (OSError, IOError, ValueError) as e:
                self.disp(
                    f"Can't read existing metadata file at {meta_file_path}, "
                    f"aborting: {e}",
                    error=True,
                )
                self.host.quit(1)
        else:
            mb_data = {} if mb_data is None else mb_data.copy()

            # in all cases, we want to remove unwanted keys
        for key in KEY_TO_REMOVE_METADATA:
            try:
                del mb_data[key]
            except KeyError:
                pass
                # and override metadata with command-line arguments
        self.setMbDataFromArgs(mb_data)

        if self.args.no_publish:
            mb_data["publish"] = False

            # then we create the file and write metadata there, as JSON dict
            # XXX: if we port jp one day on Windows, O_BINARY may need to be added here
        with os.fdopen(
            os.open(meta_file_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600), "w+b"
        ) as f:
            # we need to use an intermediate unicode buffer to write to the file
            # unicode without escaping characters
            unicode_dump = json.dumps(
                mb_data,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": "),
                sort_keys=True,
            )
            f.write(unicode_dump.encode("utf-8"))

        return mb_data, meta_file_path

    async def edit(self, content_file_path, content_file_obj, mb_data=None):
        """Edit the file contening the content using editor, and publish it"""
        # we first create metadata file
        meta_ori, meta_file_path = self.buildMetadataFile(content_file_path, mb_data)

        coroutines = []

        # do we need a preview ?
        if self.args.preview:
            self.disp("Preview requested, launching it", 1)
            # we redirect outputs to /dev/null to avoid console pollution in editor
            # if user wants to see messages, (s)he can call "blog preview" directly
            coroutines.append(
                asyncio.create_subprocess_exec(
                    sys.argv[0],
                    "blog",
                    "preview",
                    "--inotify",
                    "true",
                    "-p",
                    self.profile,
                    str(content_file_path),
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                )
            )

            # we launch editor
        coroutines.append(
            self.runEditor(
                "blog_editor_args",
                content_file_path,
                content_file_obj,
                meta_file_path=meta_file_path,
                meta_ori=meta_ori,
            )
        )

        await asyncio.gather(*coroutines)

    async def publish(self, content, mb_data):
        await self.setMbDataContent(content, mb_data)

        if self.pubsub_item:
            mb_data["id"] = self.pubsub_item

        mb_data = data_format.serialise(mb_data)

        await self.host.bridge.mbSend(
            self.pubsub_service, self.pubsub_node, mb_data, self.profile
        )
        self.disp("Blog item published")

    def getTmpSuff(self):
        # we get current syntax to determine file extension
        return SYNTAX_EXT.get(self.current_syntax, SYNTAX_EXT[""])

    async def getItemData(self, service, node, item):
        items = [item] if item else []

        mb_data = data_format.deserialise(
            await self.host.bridge.mbGet(service, node, 1, items, {}, self.profile)
        )
        item = mb_data["items"][0]

        try:
            content = item["content_xhtml"]
        except KeyError:
            content = item["content"]
            if content:
                content = await self.host.bridge.syntaxConvert(
                    content, "text", SYNTAX_XHTML, False, self.profile
                )

        if content and self.current_syntax != SYNTAX_XHTML:
            content = await self.host.bridge.syntaxConvert(
                content, SYNTAX_XHTML, self.current_syntax, False, self.profile
            )

        if content and self.current_syntax == SYNTAX_XHTML:
            content = content.strip()
            if not content.startswith("<div>"):
                content = "<div>" + content + "</div>"
            try:
                from lxml import etree
            except ImportError:
                self.disp(_("You need lxml to edit pretty XHTML"))
            else:
                parser = etree.XMLParser(remove_blank_text=True)
                root = etree.fromstring(content, parser)
                content = etree.tostring(root, encoding=str, pretty_print=True)

        return content, item, item["id"]

    async def start(self):
        # if there are user defined extension, we use them
        SYNTAX_EXT.update(
            config.getConfig(self.sat_conf, C.CONFIG_SECTION, CONF_SYNTAX_EXT, {})
        )
        self.current_syntax = await self.get_current_syntax()

        (
            self.pubsub_service,
            self.pubsub_node,
            self.pubsub_item,
            content_file_path,
            content_file_obj,
            mb_data,
        ) = await self.getItemPath()

        await self.edit(content_file_path, content_file_obj, mb_data=mb_data)
        self.host.quit()


class Rename(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "rename",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            help=_("rename an blog item"),
        )

    def add_parser_options(self):
        self.parser.add_argument("new_id", help=_("new item id to use"))

    async def start(self):
        try:
            await self.host.bridge.mbRename(
                self.args.service,
                self.args.node,
                self.args.item,
                self.args.new_id,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't rename item: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp("Item renamed")
            self.host.quit(C.EXIT_OK)


class Preview(base.CommandBase, common.BaseEdit):
    # TODO: need to be rewritten with template output

    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "preview", use_verbose=True, help=_("preview a blog content")
        )
        common.BaseEdit.__init__(self, self.host, BLOG_TMP_DIR, use_metadata=True)

    def add_parser_options(self):
        self.parser.add_argument(
            "--inotify",
            type=str,
            choices=("auto", "true", "false"),
            default="auto",
            help=_("use inotify to handle preview"),
        )
        self.parser.add_argument(
            "file",
            nargs="?",
            default="current",
            help=_("path to the content file"),
        )

    async def showPreview(self):
        # we implement showPreview here so we don't have to import webbrowser and urllib
        # when preview is not used
        url = "file:{}".format(self.urllib.parse.quote(self.preview_file_path))
        self.webbrowser.open_new_tab(url)

    async def _launchPreviewExt(self, cmd_line, opt_name):
        url = "file:{}".format(self.urllib.parse.quote(self.preview_file_path))
        args = common.parse_args(
            self.host, cmd_line, url=url, preview_file=self.preview_file_path
        )
        if not args:
            self.disp(
                'Couln\'t find command in "{name}", abording'.format(name=opt_name),
                error=True,
            )
            self.host.quit(1)
        subprocess.Popen(args)

    async def openPreviewExt(self):
        await self._launchPreviewExt(self.open_cb_cmd, "blog_preview_open_cmd")

    async def updatePreviewExt(self):
        await self._launchPreviewExt(self.update_cb_cmd, "blog_preview_update_cmd")

    async def updateContent(self):
        with self.content_file_path.open("rb") as f:
            content = f.read().decode("utf-8-sig")
            if content and self.syntax != SYNTAX_XHTML:
                # we use safe=True because we want to have a preview as close as possible
                # to what the people will see
                content = await self.host.bridge.syntaxConvert(
                    content, self.syntax, SYNTAX_XHTML, True, self.profile
                )

        xhtml = (
            f'<html xmlns="http://www.w3.org/1999/xhtml">'
            f'<head><meta http-equiv="Content-Type" content="text/html;charset=utf-8" />'
            f"</head>"
            f"<body>{content}</body>"
            f"</html>"
        )

        with open(self.preview_file_path, "wb") as f:
            f.write(xhtml.encode("utf-8"))

    async def start(self):
        import webbrowser
        import urllib.request, urllib.parse, urllib.error

        self.webbrowser, self.urllib = webbrowser, urllib

        if self.args.inotify != "false":
            try:
                import aionotify

            except ImportError:
                if self.args.inotify == "auto":
                    aionotify = None
                    self.disp(
                        f"aionotify module not found, deactivating feature. You can "
                        f"install it with {AIONOTIFY_INSTALL}"
                    )
                else:
                    self.disp(
                        f"aioinotify not found, can't activate the feature! Please "
                        f"install it with {AIONOTIFY_INSTALL}",
                        error=True,
                    )
                    self.host.quit(1)
        else:
            aionotify = None

        sat_conf = self.sat_conf
        SYNTAX_EXT.update(
            config.getConfig(sat_conf, C.CONFIG_SECTION, CONF_SYNTAX_EXT, {})
        )

        try:
            self.open_cb_cmd = config.getConfig(
                sat_conf, C.CONFIG_SECTION, "blog_preview_open_cmd", Exception
            )
        except (NoOptionError, NoSectionError):
            self.open_cb_cmd = None
            open_cb = self.showPreview
        else:
            open_cb = self.openPreviewExt

        self.update_cb_cmd = config.getConfig(
            sat_conf, C.CONFIG_SECTION, "blog_preview_update_cmd", self.open_cb_cmd
        )
        if self.update_cb_cmd is None:
            update_cb = self.showPreview
        else:
            update_cb = self.updatePreviewExt

            # which file do we need to edit?
        if self.args.file == "current":
            self.content_file_path = self.getCurrentFile(self.profile)
        else:
            try:
                self.content_file_path = Path(self.args.file).resolve(strict=True)
            except FileNotFoundError:
                self.disp(_('File "{file}" doesn\'t exist!').format(file=self.args.file))
                self.host.quit(C.EXIT_NOT_FOUND)

        self.syntax = await guessSyntaxFromPath(
            self.host, sat_conf, self.content_file_path
        )

        # at this point the syntax is converted, we can display the preview
        preview_file = tempfile.NamedTemporaryFile(suffix=".xhtml", delete=False)
        self.preview_file_path = preview_file.name
        preview_file.close()
        await self.updateContent()

        if aionotify is None:
            # XXX: we don't delete file automatically because browser needs it
            #      (and webbrowser.open can return before it is read)
            self.disp(
                f"temporary file created at {self.preview_file_path}\nthis file will NOT "
                f"BE DELETED AUTOMATICALLY, please delete it yourself when you have "
                f"finished"
            )
            await open_cb()
        else:
            await open_cb()
            watcher = aionotify.Watcher()
            watcher_kwargs = {
                # Watcher don't accept Path so we convert to string
                "path": str(self.content_file_path),
                "alias": "content_file",
                "flags": aionotify.Flags.CLOSE_WRITE
                | aionotify.Flags.DELETE_SELF
                | aionotify.Flags.MOVE_SELF,
            }
            watcher.watch(**watcher_kwargs)

            loop = asyncio.get_event_loop()
            await watcher.setup(loop)

            try:
                while True:
                    event = await watcher.get_event()
                    self.disp("Content updated", 1)
                    if event.flags & (
                        aionotify.Flags.DELETE_SELF | aionotify.Flags.MOVE_SELF
                    ):
                        self.disp(
                            "DELETE/MOVE event catched, changing the watch",
                            2,
                        )
                        try:
                            watcher.unwatch("content_file")
                        except IOError as e:
                            self.disp(
                                f"Can't remove the watch: {e}",
                                2,
                            )
                        watcher = aionotify.Watcher()
                        watcher.watch(**watcher_kwargs)
                        try:
                            await watcher.setup(loop)
                        except OSError:
                            # if the new file is not here yet we can have an error
                            # as a workaround, we do a little rest and try again
                            await asyncio.sleep(1)
                            await watcher.setup(loop)
                    await self.updateContent()
                    await update_cb()
            except FileNotFoundError:
                self.disp("The file seems to have been deleted.", error=True)
                self.host.quit(C.EXIT_NOT_FOUND)
            finally:
                os.unlink(self.preview_file_path)
                try:
                    watcher.unwatch("content_file")
                except IOError as e:
                    self.disp(
                        f"Can't remove the watch: {e}",
                        2,
                    )


class Import(base.CommandBase):
    def __init__(self, host):
        super(Import, self).__init__(
            host,
            "import",
            use_pubsub=True,
            use_progress=True,
            help=_("import an external blog"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "importer",
            nargs="?",
            help=_("importer name, nothing to display importers list"),
        )
        self.parser.add_argument("--host", help=_("original blog host"))
        self.parser.add_argument(
            "--no-images-upload",
            action="store_true",
            help=_("do *NOT* upload images (default: do upload images)"),
        )
        self.parser.add_argument(
            "--upload-ignore-host",
            help=_("do not upload images from this host (default: upload all images)"),
        )
        self.parser.add_argument(
            "--ignore-tls-errors",
            action="store_true",
            help=_("ignore invalide TLS certificate for uploads"),
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
            "location",
            nargs="?",
            help=_(
                "importer data location (see importer description), nothing to show "
                "importer description"
            ),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("Blog upload started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("Blog uploaded successfully"), 2)
        redirections = {
            k[len(URL_REDIRECT_PREFIX) :]: v
            for k, v in metadata.items()
            if k.startswith(URL_REDIRECT_PREFIX)
        }
        if redirections:
            conf = "\n".join(
                [
                    "url_redirections_dict = {}".format(
                        # we need to add ' ' before each new line
                        # and to double each '%' for ConfigParser
                        "\n ".join(
                            json.dumps(redirections, indent=1, separators=(",", ": "))
                            .replace("%", "%%")
                            .split("\n")
                        )
                    ),
                ]
            )
            self.disp(
                _(
                    "\nTo redirect old URLs to new ones, put the following lines in your"
                    " sat.conf file, in [libervia] section:\n\n{conf}"
                ).format(conf=conf)
            )

    async def onProgressError(self, error_msg):
        self.disp(
            _("Error while uploading blog: {error_msg}").format(error_msg=error_msg),
            error=True,
        )

    async def start(self):
        if self.args.location is None:
            for name in ("option", "service", "no_images_upload"):
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
                            for name, desc in await self.host.bridge.blogImportList()
                        ]
                    )
                )
            else:
                try:
                    short_desc, long_desc = await self.host.bridge.blogImportDesc(
                        self.args.importer
                    )
                except Exception as e:
                    msg = [l for l in str(e).split("\n") if l][
                        -1
                    ]  # we only keep the last line
                    self.disp(msg)
                    self.host.quit(1)
                else:
                    self.disp(f"{self.args.importer}: {short_desc}\n\n{long_desc}")
            self.host.quit()
        else:
            # we have a location, an import is requested
            options = {key: value for key, value in self.args.option}
            if self.args.host:
                options["host"] = self.args.host
            if self.args.ignore_tls_errors:
                options["ignore_tls_errors"] = C.BOOL_TRUE
            if self.args.no_images_upload:
                options["upload_images"] = C.BOOL_FALSE
                if self.args.upload_ignore_host:
                    self.parser.error(
                        "upload-ignore-host option can't be used when no-images-upload "
                        "is set"
                    )
            elif self.args.upload_ignore_host:
                options["upload_ignore_host"] = self.args.upload_ignore_host

            try:
                progress_id = await self.host.bridge.blogImport(
                    self.args.importer,
                    self.args.location,
                    options,
                    self.args.service,
                    self.args.node,
                    self.profile,
                )
            except Exception as e:
                self.disp(
                    _("Error while trying to import a blog: {e}").format(e=e),
                    error=True,
                )
                self.host.quit(1)

            await self.set_progress_id(progress_id)


class Blog(base.CommandBase):
    subcommands = (Set, Get, Edit, Rename, Preview, Import)

    def __init__(self, host):
        super(Blog, self).__init__(
            host, "blog", use_profile=False, help=_("blog/microblog management")
        )
