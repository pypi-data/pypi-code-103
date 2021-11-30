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
import os.path
import time
import tempfile
import asyncio
import shlex
import re
from pathlib import Path
from sat_frontends.jp.constants import Const as C
from sat.core.i18n import _
from sat.core import exceptions
from sat.tools.common import regex
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import uri as xmpp_uri
from sat.tools import config
from configparser import NoSectionError, NoOptionError
from collections import namedtuple

# default arguments used for some known editors (editing with metadata)
VIM_SPLIT_ARGS = "-c 'set nospr|vsplit|wincmd w|next|wincmd w'"
EMACS_SPLIT_ARGS = '--eval "(split-window-horizontally)"'
EDITOR_ARGS_MAGIC = {
    "vim": VIM_SPLIT_ARGS + " {content_file} {metadata_file}",
    "nvim": VIM_SPLIT_ARGS + " {content_file} {metadata_file}",
    "gvim": VIM_SPLIT_ARGS + " --nofork {content_file} {metadata_file}",
    "emacs": EMACS_SPLIT_ARGS + " {content_file} {metadata_file}",
    "xemacs": EMACS_SPLIT_ARGS + " {content_file} {metadata_file}",
    "nano": " -F {content_file} {metadata_file}",
}

SECURE_UNLINK_MAX = 10
SECURE_UNLINK_DIR = ".backup"
METADATA_SUFF = "_metadata.json"


def ansi_ljust(s, width):
    """ljust method handling ANSI escape codes"""
    cleaned = regex.ansiRemove(s)
    return s + " " * (width - len(cleaned))


def ansi_center(s, width):
    """ljust method handling ANSI escape codes"""
    cleaned = regex.ansiRemove(s)
    diff = width - len(cleaned)
    half = diff / 2
    return half * " " + s + (half + diff % 2) * " "


def ansi_rjust(s, width):
    """ljust method handling ANSI escape codes"""
    cleaned = regex.ansiRemove(s)
    return " " * (width - len(cleaned)) + s


def getTmpDir(sat_conf, cat_dir, sub_dir=None):
    """Return directory used to store temporary files

    @param sat_conf(ConfigParser.ConfigParser): instance opened on sat configuration
    @param cat_dir(str): directory of the category (e.g. "blog")
    @param sub_dir(str): sub directory where data need to be put
        profile can be used here, or special directory name
        sub_dir will be escaped to be usable in path (use regex.pathUnescape to find
        initial str)
    @return (Path): path to the dir
    """
    local_dir = config.getConfig(sat_conf, "", "local_dir", Exception)
    path_elts = [local_dir, cat_dir]
    if sub_dir is not None:
        path_elts.append(regex.pathEscape(sub_dir))
    return Path(*path_elts)


def parse_args(host, cmd_line, **format_kw):
    """Parse command arguments

    @param cmd_line(unicode): command line as found in sat.conf
    @param format_kw: keywords used for formating
    @return (list(unicode)): list of arguments to pass to subprocess function
    """
    try:
        # we split the arguments and add the known fields
        # we split arguments first to avoid escaping issues in file names
        return [a.format(**format_kw) for a in shlex.split(cmd_line)]
    except ValueError as e:
        host.disp(
            "Couldn't parse editor cmd [{cmd}]: {reason}".format(cmd=cmd_line, reason=e)
        )
        return []


class BaseEdit(object):
    """base class for editing commands

    This class allows to edit file for PubSub or something else.
    It works with temporary files in SàT local_dir, in a "cat_dir" subdir
    """

    def __init__(self, host, cat_dir, use_metadata=False):
        """
        @param sat_conf(ConfigParser.ConfigParser): instance opened on sat configuration
        @param cat_dir(unicode): directory to use for drafts
            this will be a sub-directory of SàT's local_dir
        @param use_metadata(bool): True is edition need a second file for metadata
            most of signature change with use_metadata with an additional metadata
            argument.
            This is done to raise error if a command needs metadata but forget the flag,
            and vice versa
        """
        self.host = host
        self.cat_dir = cat_dir
        self.use_metadata = use_metadata

    def secureUnlink(self, path):
        """Unlink given path after keeping it for a while

        This method is used to prevent accidental deletion of a draft
        If there are more file in SECURE_UNLINK_DIR than SECURE_UNLINK_MAX,
        older file are deleted
        @param path(Path, str): file to unlink
        """
        path = Path(path).resolve()
        if not path.is_file:
            raise OSError("path must link to a regular file")
        if path.parent != getTmpDir(self.sat_conf, self.cat_dir):
            self.disp(
                f"File {path} is not in SàT temporary hierarchy, we do not remove " f"it",
                2,
            )
            return
            # we have 2 files per draft with use_metadata, so we double max
        unlink_max = SECURE_UNLINK_MAX * 2 if self.use_metadata else SECURE_UNLINK_MAX
        backup_dir = getTmpDir(self.sat_conf, self.cat_dir, SECURE_UNLINK_DIR)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        filename = os.path.basename(path)
        backup_path = os.path.join(backup_dir, filename)
        # we move file to backup dir
        self.host.disp(
            "Backuping file {src} to {dst}".format(src=path, dst=backup_path),
            1,
        )
        os.rename(path, backup_path)
        # and if we exceeded the limit, we remove older file
        backup_files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)]
        if len(backup_files) > unlink_max:
            backup_files.sort(key=lambda path: os.stat(path).st_mtime)
            for path in backup_files[: len(backup_files) - unlink_max]:
                self.host.disp("Purging backup file {}".format(path), 2)
                os.unlink(path)

    async def runEditor(
        self,
        editor_args_opt,
        content_file_path,
        content_file_obj,
        meta_file_path=None,
        meta_ori=None,
    ):
        """Run editor to edit content and metadata

        @param editor_args_opt(unicode): option in [jp] section in configuration for
            specific args
        @param content_file_path(str): path to the content file
        @param content_file_obj(file): opened file instance
        @param meta_file_path(str, Path, None): metadata file path
            if None metadata will not be used
        @param meta_ori(dict, None): original cotent of metadata
            can't be used if use_metadata is False
        """
        if not self.use_metadata:
            assert meta_file_path is None
            assert meta_ori is None

            # we calculate hashes to check for modifications
        import hashlib

        content_file_obj.seek(0)
        tmp_ori_hash = hashlib.sha1(content_file_obj.read()).digest()
        content_file_obj.close()

        # we prepare arguments
        editor = config.getConfig(self.sat_conf, C.CONFIG_SECTION, "editor") or os.getenv(
            "EDITOR", "vi"
        )
        try:
            # is there custom arguments in sat.conf ?
            editor_args = config.getConfig(
                self.sat_conf, C.CONFIG_SECTION, editor_args_opt, Exception
            )
        except (NoOptionError, NoSectionError):
            # no, we check if we know the editor and have special arguments
            if self.use_metadata:
                editor_args = EDITOR_ARGS_MAGIC.get(os.path.basename(editor), "")
            else:
                editor_args = ""
        parse_kwargs = {"content_file": content_file_path}
        if self.use_metadata:
            parse_kwargs["metadata_file"] = meta_file_path
        args = parse_args(self.host, editor_args, **parse_kwargs)
        if not args:
            args = [content_file_path]

            # actual editing
        editor_process = await asyncio.create_subprocess_exec(
            editor, *[str(a) for a in args]
        )
        editor_exit = await editor_process.wait()

        # edition will now be checked, and data will be sent if it was a success
        if editor_exit != 0:
            self.disp(
                f"Editor exited with an error code, so temporary file has not be "
                f"deleted, and item is not published.\nYou can find temporary file "
                f"at {content_file_path}",
                error=True,
            )
        else:
            # main content
            try:
                with content_file_path.open("rb") as f:
                    content = f.read()
            except (OSError, IOError):
                self.disp(
                    f"Can read file at {content_file_path}, have it been deleted?\n"
                    f"Cancelling edition",
                    error=True,
                )
                self.host.quit(C.EXIT_NOT_FOUND)

                # metadata
            if self.use_metadata:
                try:
                    with meta_file_path.open("rb") as f:
                        metadata = json.load(f)
                except (OSError, IOError):
                    self.disp(
                        f"Can read file at {meta_file_path}, have it been deleted?\n"
                        f"Cancelling edition",
                        error=True,
                    )
                    self.host.quit(C.EXIT_NOT_FOUND)
                except ValueError:
                    self.disp(
                        f"Can't parse metadata, please check it is correct JSON format. "
                        f"Cancelling edition.\nYou can find tmp file at "
                        f"{content_file_path} and temporary meta file at "
                        f"{meta_file_path}.",
                        error=True,
                    )
                    self.host.quit(C.EXIT_DATA_ERROR)

            if self.use_metadata and not metadata.get("publish", True):
                self.disp(
                    f'Publication blocked by "publish" key in metadata, cancelling '
                    f"edition.\n\ntemporary file path:\t{content_file_path}\nmetadata "
                    f"file path:\t{meta_file_path}",
                    error=True,
                )
                self.host.quit()

            if len(content) == 0:
                self.disp("Content is empty, cancelling the edition")
                if content_file_path.parent != getTmpDir(self.sat_conf, self.cat_dir):
                    self.disp(
                        "File are not in SàT temporary hierarchy, we do not remove them",
                        2,
                    )
                    self.host.quit()
                self.disp(f"Deletion of {content_file_path}", 2)
                os.unlink(content_file_path)
                if self.use_metadata:
                    self.disp(f"Deletion of {meta_file_path}".format(meta_file_path), 2)
                    os.unlink(meta_file_path)
                self.host.quit()

                # time to re-check the hash
            elif tmp_ori_hash == hashlib.sha1(content).digest() and (
                not self.use_metadata or meta_ori == metadata
            ):
                self.disp("The content has not been modified, cancelling the edition")
                self.host.quit()

            else:
                # we can now send the item
                content = content.decode("utf-8-sig")  # we use utf-8-sig to avoid BOM
                try:
                    if self.use_metadata:
                        await self.publish(content, metadata)
                    else:
                        await self.publish(content)
                except Exception as e:
                    if self.use_metadata:
                        self.disp(
                            f"Error while sending your item, the temporary files have "
                            f"been kept at {content_file_path} and {meta_file_path}: "
                            f"{e}",
                            error=True,
                        )
                    else:
                        self.disp(
                            f"Error while sending your item, the temporary file has been "
                            f"kept at {content_file_path}: {e}",
                            error=True,
                        )
                    self.host.quit(1)

            self.secureUnlink(content_file_path)
            if self.use_metadata:
                self.secureUnlink(meta_file_path)

    async def publish(self, content):
        # if metadata is needed, publish will be called with it last argument
        raise NotImplementedError

    def getTmpFile(self):
        """Create a temporary file

        @return (tuple(file, Path)): opened (w+b) file object and file path
        """
        suff = "." + self.getTmpSuff()
        cat_dir_str = self.cat_dir
        tmp_dir = getTmpDir(self.sat_conf, self.cat_dir, self.profile)
        if not tmp_dir.exists():
            try:
                tmp_dir.mkdir(parents=True)
            except OSError as e:
                self.disp(
                    f"Can't create {tmp_dir} directory: {e}",
                    error=True,
                )
                self.host.quit(1)
        try:
            fd, path = tempfile.mkstemp(
                suffix=suff,
                prefix=time.strftime(cat_dir_str + "_%Y-%m-%d_%H:%M:%S_"),
                dir=tmp_dir,
                text=True,
            )
            return os.fdopen(fd, "w+b"), Path(path)
        except OSError as e:
            self.disp(f"Can't create temporary file: {e}", error=True)
            self.host.quit(1)

    def getCurrentFile(self, profile):
        """Get most recently edited file

        @param profile(unicode): profile linked to the draft
        @return(Path): full path of current file
        """
        # we guess the item currently edited by choosing
        # the most recent file corresponding to temp file pattern
        # in tmp_dir, excluding metadata files
        tmp_dir = getTmpDir(self.sat_conf, self.cat_dir, profile)
        available = [
            p
            for p in tmp_dir.glob(f"{self.cat_dir}_*")
            if not p.match(f"*{METADATA_SUFF}")
        ]
        if not available:
            self.disp(
                f"Could not find any content draft in {tmp_dir}",
                error=True,
            )
            self.host.quit(1)
        return max(available, key=lambda p: p.stat().st_mtime)

    async def getItemData(self, service, node, item):
        """return formatted content, metadata (or not if use_metadata is false), and item id"""
        raise NotImplementedError

    def getTmpSuff(self):
        """return suffix used for content file"""
        return "xml"

    async def getItemPath(self):
        """Retrieve item path (i.e. service and node) from item argument

        This method is obviously only useful for edition of PubSub based features
        """
        service = self.args.service
        node = self.args.node
        item = self.args.item
        last_item = self.args.last_item

        if self.args.current:
            # user wants to continue current draft
            content_file_path = self.getCurrentFile(self.profile)
            self.disp("Continuing edition of current draft", 2)
            content_file_obj = content_file_path.open("r+b")
            # we seek at the end of file in case of an item already exist
            # this will write content of the existing item at the end of the draft.
            # This way no data should be lost.
            content_file_obj.seek(0, os.SEEK_END)
        elif self.args.draft_path:
            # there is an existing draft that we use
            content_file_path = self.args.draft_path.expanduser()
            content_file_obj = content_file_path.open("r+b")
            # we seek at the end for the same reason as above
            content_file_obj.seek(0, os.SEEK_END)
        else:
            # we need a temporary file
            content_file_obj, content_file_path = self.getTmpFile()

        if item or last_item:
            self.disp("Editing requested published item", 2)
            try:
                if self.use_metadata:
                    content, metadata, item = await self.getItemData(service, node, item)
                else:
                    content, item = await self.getItemData(service, node, item)
            except Exception as e:
                # FIXME: ugly but we have not good may to check errors in bridge
                if "item-not-found" in str(e):
                    #  item doesn't exist, we create a new one with requested id
                    metadata = None
                    if last_item:
                        self.disp(_("no item found at all, we create a new one"), 2)
                    else:
                        self.disp(
                            _(
                                'item "{item}" not found, we create a new item with'
                                "this id"
                            ).format(item=item),
                            2,
                        )
                    content_file_obj.seek(0)
                else:
                    self.disp(f"Error while retrieving item: {e}")
                    self.host.quit(C.EXIT_ERROR)
            else:
                # item exists, we write content
                if content_file_obj.tell() != 0:
                    # we already have a draft,
                    # we copy item content after it and add an indicator
                    content_file_obj.write("\n*****\n")
                content_file_obj.write(content.encode("utf-8"))
                content_file_obj.seek(0)
                self.disp(_('item "{item}" found, we edit it').format(item=item), 2)
        else:
            self.disp("Editing a new item", 2)
            if self.use_metadata:
                metadata = None

        if self.use_metadata:
            return service, node, item, content_file_path, content_file_obj, metadata
        else:
            return service, node, item, content_file_path, content_file_obj


class Table(object):
    def __init__(self, host, data, headers=None, filters=None, use_buffer=False):
        """
        @param data(iterable[list]): table data
            all lines must have the same number of columns
        @param headers(iterable[unicode], None): names/titles of the columns
            if not None, must have same number of columns as data
        @param filters(iterable[(callable, unicode)], None): values filters
            the callable will get 2 arguments:
                - current column value
                - RowData with all columns values
            if may also only use 1 argument, which will then be current col value.
            the callable must return a string
            if it's unicode, it will be used with .format and must countain u'{}' which
            will be replaced with the string.
            if not None, must have same number of columns as data
        @param use_buffer(bool): if True, bufferise output instead of printing it directly
        """
        self.host = host
        self._buffer = [] if use_buffer else None
        #  headers are columns names/titles, can be None
        self.headers = headers
        #  sizes fof columns without headers,
        # headers may be larger
        self.sizes = []
        #  rows countains one list per row with columns values
        self.rows = []

        size = None
        if headers:
            # we use a namedtuple to make the value easily accessible from filters
            headers_safe = [re.sub(r"[^a-zA-Z_]", "_", h) for h in headers]
            row_cls = namedtuple("RowData", headers_safe)
        else:
            row_cls = tuple

        for row_data in data:
            new_row = []
            row_data_list = list(row_data)
            for idx, value in enumerate(row_data_list):
                if filters is not None and filters[idx] is not None:
                    filter_ = filters[idx]
                    if isinstance(filter_, str):
                        col_value = filter_.format(value)
                    else:
                        try:
                            col_value = filter_(value, row_cls(*row_data_list))
                        except TypeError:
                            col_value = filter_(value)
                            # we count size without ANSI code as they will change length of the
                            # string when it's mostly style/color changes.
                    col_size = len(regex.ansiRemove(col_value))
                else:
                    col_value = str(value)
                    col_size = len(col_value)
                new_row.append(col_value)
                if size is None:
                    self.sizes.append(col_size)
                else:
                    self.sizes[idx] = max(self.sizes[idx], col_size)
            if size is None:
                size = len(new_row)
                if headers is not None and len(headers) != size:
                    raise exceptions.DataError("headers size is not coherent with rows")
            else:
                if len(new_row) != size:
                    raise exceptions.DataError("rows size is not coherent")
            self.rows.append(new_row)

        if not data and headers is not None:
            #  the table is empty, we print headers at their lenght
            self.sizes = [len(h) for h in headers]

    @property
    def string(self):
        if self._buffer is None:
            raise exceptions.InternalError("buffer must be used to get a string")
        return "\n".join(self._buffer)

    @staticmethod
    def readDictValues(data, keys, defaults=None):
        if defaults is None:
            defaults = {}
        for key in keys:
            try:
                yield data[key]
            except KeyError as e:
                default = defaults.get(key)
                if default is not None:
                    yield default
                else:
                    raise e

    @classmethod
    def fromListDict(
        cls, host, data, keys=None, headers=None, filters=None, defaults=None
    ):
        """Create a table from a list of dictionaries

        each dictionary is a row of the table, keys being columns names.
        the whole data will be read and kept into memory, to be printed
        @param data(list[dict[unicode, unicode]]): data to create the table from
        @param keys(iterable[unicode], None): keys to get
            if None, all keys will be used
        @param headers(iterable[unicode], None): name of the columns
            names must be in same order as keys
        @param filters(dict[unicode, (callable,unicode)), None): filter to use on values
            keys correspond to keys to filter, and value is the same as for Table.__init__
        @param defaults(dict[unicode, unicode]): default value to use
            if None, an exception will be raised if not value is found
        """
        if keys is None and headers is not None:
            # FIXME: keys are not needed with OrderedDict,
            raise exceptions.DataError("You must specify keys order to used headers")
        if keys is None:
            keys = list(data[0].keys())
        if headers is None:
            headers = keys
        if filters is None:
            filters = {}
        filters = [filters.get(k) for k in keys]
        return cls(
            host, (cls.readDictValues(d, keys, defaults) for d in data), headers, filters
        )

    def _headers(self, head_sep, headers, sizes, alignment="left", style=None):
        """Render headers

        @param head_sep(unicode): sequence to use as separator
        @param alignment(unicode): how to align, can be left, center or right
        @param style(unicode, iterable[unicode], None): ANSI escape sequences to apply
        @param headers(list[unicode]): headers to show
        @param sizes(list[int]): sizes of columns
        """
        rendered_headers = []
        if isinstance(style, str):
            style = [style]
        for idx, header in enumerate(headers):
            size = sizes[idx]
            if alignment == "left":
                rendered = header[:size].ljust(size)
            elif alignment == "center":
                rendered = header[:size].center(size)
            elif alignment == "right":
                rendered = header[:size].rjust(size)
            else:
                raise exceptions.InternalError("bad alignment argument")
            if style:
                args = style + [rendered]
                rendered = A.color(*args)
            rendered_headers.append(rendered)
        return head_sep.join(rendered_headers)

    def _disp(self, data):
        """output data (can be either bufferised or printed)"""
        if self._buffer is not None:
            self._buffer.append(data)
        else:
            self.host.disp(data)

    def display(
        self,
        head_alignment="left",
        columns_alignment="left",
        head_style=None,
        show_header=True,
        show_borders=True,
        hide_cols=None,
        col_sep=" │ ",
        top_left="┌",
        top="─",
        top_sep="─┬─",
        top_right="┐",
        left="│",
        right=None,
        head_sep=None,
        head_line="┄",
        head_line_left="├",
        head_line_sep="┄┼┄",
        head_line_right="┤",
        bottom_left="└",
        bottom=None,
        bottom_sep="─┴─",
        bottom_right="┘",
    ):
        """Print the table

        @param show_header(bool): True if header need no be shown
        @param show_borders(bool): True if borders need no be shown
        @param hide_cols(None, iterable(unicode)): columns which should not be displayed
        @param head_alignment(unicode): how to align headers, can be left, center or right
        @param columns_alignment(unicode): how to align columns, can be left, center or
            right
        @param col_sep(unicode): separator betweens columns
        @param head_line(unicode): character to use to make line under head
        @param disp(callable, None): method to use to display the table
            None to use self.host.disp
        """
        if not self.sizes:
            # the table is empty
            return
        col_sep_size = len(regex.ansiRemove(col_sep))

        # if we have columns to hide, we remove them from headers and size
        if not hide_cols:
            headers = self.headers
            sizes = self.sizes
        else:
            headers = list(self.headers)
            sizes = self.sizes[:]
            ignore_idx = [headers.index(to_hide) for to_hide in hide_cols]
            for to_hide in hide_cols:
                hide_idx = headers.index(to_hide)
                del headers[hide_idx]
                del sizes[hide_idx]

        if right is None:
            right = left
        if top_sep is None:
            top_sep = col_sep_size * top
        if head_sep is None:
            head_sep = col_sep
        if bottom is None:
            bottom = top
        if bottom_sep is None:
            bottom_sep = col_sep_size * bottom
        if not show_borders:
            left = right = head_line_left = head_line_right = ""
            # top border
        if show_borders:
            self._disp(
                top_left + top_sep.join([top * size for size in sizes]) + top_right
            )

            # headers
        if show_header and self.headers is not None:
            self._disp(
                left
                + self._headers(head_sep, headers, sizes, head_alignment, head_style)
                + right
            )
            # header line
            self._disp(
                head_line_left
                + head_line_sep.join([head_line * size for size in sizes])
                + head_line_right
            )

            # content
        if columns_alignment == "left":
            alignment = lambda idx, s: ansi_ljust(s, sizes[idx])
        elif columns_alignment == "center":
            alignment = lambda idx, s: ansi_center(s, sizes[idx])
        elif columns_alignment == "right":
            alignment = lambda idx, s: ansi_rjust(s, sizes[idx])
        else:
            raise exceptions.InternalError("bad columns alignment argument")

        for row in self.rows:
            if hide_cols:
                row = [v for idx, v in enumerate(row) if idx not in ignore_idx]
            self._disp(
                left
                + col_sep.join([alignment(idx, c) for idx, c in enumerate(row)])
                + right
            )

        if show_borders:
            # bottom border
            self._disp(
                bottom_left
                + bottom_sep.join([bottom * size for size in sizes])
                + bottom_right
            )
            #  we return self so string can be used after display (table.display().string)
        return self

    def display_blank(self, **kwargs):
        """Display table without visible borders"""
        kwargs_ = {"col_sep": " ", "head_line_sep": " ", "show_borders": False}
        kwargs_.update(kwargs)
        return self.display(**kwargs_)


async def fill_well_known_uri(command, path, key, meta_map=None):
    """Look for URIs in well-known location and fill appropriate args if suitable

    @param command(CommandBase): command instance
        args of this instance will be updated with found values
    @param path(unicode): absolute path to use as a starting point to look for URIs
    @param key(unicode): key to look for
    @param meta_map(dict, None): if not None, map metadata to arg name
        key is metadata used attribute name
        value is name to actually use, or None to ignore
        use empty dict to only retrieve URI
        possible keys are currently:
            - labels
    """
    args = command.args
    if args.service or args.node:
        # we only look for URIs if a service and a node are not already specified
        return

    host = command.host

    try:
        uris_data = await host.bridge.URIFind(path, [key])
    except Exception as e:
        host.disp(f"can't find {key} URI: {e}", error=True)
        host.quit(C.EXIT_BRIDGE_ERRBACK)

    try:
        uri_data = uris_data[key]
    except KeyError:
        host.disp(
            _(
                "No {key} URI specified for this project, please specify service and "
                "node"
            ).format(key=key),
            error=True,
        )
        host.quit(C.EXIT_NOT_FOUND)

    uri = uri_data["uri"]

    # set extra metadata if they are specified
    for data_key in ["labels"]:
        new_values_json = uri_data.get(data_key)
        if uri_data is not None:
            if meta_map is None:
                dest = data_key
            else:
                dest = meta_map.get(data_key)
                if dest is None:
                    continue

            try:
                values = getattr(args, data_key)
            except AttributeError:
                raise exceptions.InternalError(f"there is no {data_key!r} arguments")
            else:
                if values is None:
                    values = []
                values.extend(json.loads(new_values_json))
                setattr(args, dest, values)

    parsed_uri = xmpp_uri.parseXMPPUri(uri)
    try:
        args.service = parsed_uri["path"]
        args.node = parsed_uri["node"]
    except KeyError:
        host.disp(_("Invalid URI found: {uri}").format(uri=uri), error=True)
        host.quit(C.EXIT_DATA_ERROR)
