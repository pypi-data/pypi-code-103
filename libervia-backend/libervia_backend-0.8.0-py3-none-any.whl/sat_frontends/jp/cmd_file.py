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
from . import xmlui_manager
import sys
import os
import os.path
import tarfile
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat_frontends.tools import jid
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import utils
from urllib.parse import urlparse
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET  # FIXME: used temporarily to manage XMLUI
import json

__commands__ = ["File"]


class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(
            host,
            "send",
            use_progress=True,
            use_verbose=True,
            help=_("send a file to a contact"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "files", type=str, nargs="+", metavar="file", help=_("a list of file")
        )
        self.parser.add_argument("jid", help=_("the destination jid"))
        self.parser.add_argument(
            "-b", "--bz2", action="store_true", help=_("make a bzip2 tarball")
        )
        self.parser.add_argument(
            "-d",
            "--path",
            help=("path to the directory where the file must be stored"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            help=("namespace of the file"),
        )
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help=("name to use (DEFAULT: use source file name)"),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("File copy started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("File sent successfully"), 2)

    async def onProgressError(self, error_msg):
        if error_msg == C.PROGRESS_ERROR_DECLINED:
            self.disp(_("The file has been refused by your contact"))
        else:
            self.disp(_("Error while sending file: {}").format(error_msg), error=True)

    async def gotId(self, data, file_):
        """Called when a progress id has been received

        @param pid(unicode): progress id
        @param file_(str): file path
        """
        # FIXME: this show progress only for last progress_id
        self.disp(_("File request sent to {jid}".format(jid=self.args.jid)), 1)
        try:
            await self.set_progress_id(data["progress"])
        except KeyError:
            # TODO: if 'xmlui' key is present, manage xmlui message display
            self.disp(_("Can't send file to {jid}".format(jid=self.args.jid)), error=True)
            self.host.quit(2)

    async def start(self):
        for file_ in self.args.files:
            if not os.path.exists(file_):
                self.disp(
                    _("file {file_} doesn't exist!").format(file_=repr(file_)), error=True
                )
                self.host.quit(C.EXIT_BAD_ARG)
            if not self.args.bz2 and os.path.isdir(file_):
                self.disp(
                    _(
                        "{file_} is a dir! Please send files inside or use compression"
                    ).format(file_=repr(file_))
                )
                self.host.quit(C.EXIT_BAD_ARG)

        extra = {}
        if self.args.path:
            extra["path"] = self.args.path
        if self.args.namespace:
            extra["namespace"] = self.args.namespace

        if self.args.bz2:
            with tempfile.NamedTemporaryFile("wb", delete=False) as buf:
                self.host.addOnQuitCallback(os.unlink, buf.name)
                self.disp(_("bz2 is an experimental option, use with caution"))
                # FIXME: check free space
                self.disp(_("Starting compression, please wait..."))
                sys.stdout.flush()
                bz2 = tarfile.open(mode="w:bz2", fileobj=buf)
                archive_name = "{}.tar.bz2".format(
                    os.path.basename(self.args.files[0]) or "compressed_files"
                )
                for file_ in self.args.files:
                    self.disp(_("Adding {}").format(file_), 1)
                    bz2.add(file_)
                bz2.close()
                self.disp(_("Done !"), 1)

                try:
                    send_data = await self.host.bridge.fileSend(
                        self.args.jid,
                        buf.name,
                        self.args.name or archive_name,
                        "",
                        extra,
                        self.profile,
                    )
                except Exception as e:
                    self.disp(f"can't send file: {e}", error=True)
                    self.host.quit(C.EXIT_BRIDGE_ERRBACK)
                else:
                    await self.gotId(send_data, file_)
        else:
            for file_ in self.args.files:
                path = os.path.abspath(file_)
                try:
                    send_data = await self.host.bridge.fileSend(
                        self.args.jid,
                        path,
                        self.args.name,
                        "",
                        extra,
                        self.profile,
                    )
                except Exception as e:
                    self.disp(f"can't send file {file_!r}: {e}", error=True)
                    self.host.quit(C.EXIT_BRIDGE_ERRBACK)
                else:
                    await self.gotId(send_data, file_)


class Request(base.CommandBase):
    def __init__(self, host):
        super(Request, self).__init__(
            host,
            "request",
            use_progress=True,
            use_verbose=True,
            help=_("request a file from a contact"),
        )

    @property
    def filename(self):
        return self.args.name or self.args.hash or "output"

    def add_parser_options(self):
        self.parser.add_argument("jid", help=_("the destination jid"))
        self.parser.add_argument(
            "-D",
            "--dest",
            help=_(
                "destination path where the file will be saved (default: "
                "[current_dir]/[name|hash])"
            ),
        )
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help=_("name of the file"),
        )
        self.parser.add_argument(
            "-H",
            "--hash",
            default="",
            help=_("hash of the file"),
        )
        self.parser.add_argument(
            "-a",
            "--hash-algo",
            default="sha-256",
            help=_("hash algorithm use for --hash (default: sha-256)"),
        )
        self.parser.add_argument(
            "-d",
            "--path",
            help=("path to the directory containing the file"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            help=("namespace of the file"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("overwrite existing file without confirmation"),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("File copy started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("File received successfully"), 2)

    async def onProgressError(self, error_msg):
        if error_msg == C.PROGRESS_ERROR_DECLINED:
            self.disp(_("The file request has been refused"))
        else:
            self.disp(_("Error while requesting file: {}").format(error_msg), error=True)

    async def start(self):
        if not self.args.name and not self.args.hash:
            self.parser.error(_("at least one of --name or --hash must be provided"))
        if self.args.dest:
            path = os.path.abspath(os.path.expanduser(self.args.dest))
            if os.path.isdir(path):
                path = os.path.join(path, self.filename)
        else:
            path = os.path.abspath(self.filename)

        if os.path.exists(path) and not self.args.force:
            message = _("File {path} already exists! Do you want to overwrite?").format(
                path=path
            )
            await self.host.confirmOrQuit(message, _("file request cancelled"))

        self.full_dest_jid = await self.host.get_full_jid(self.args.jid)
        extra = {}
        if self.args.path:
            extra["path"] = self.args.path
        if self.args.namespace:
            extra["namespace"] = self.args.namespace
        try:
            progress_id = await self.host.bridge.fileJingleRequest(
                self.full_dest_jid,
                path,
                self.args.name,
                self.args.hash,
                self.args.hash_algo if self.args.hash else "",
                extra,
                self.profile,
            )
        except Exception as e:
            self.disp(msg=_("can't request file: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.set_progress_id(progress_id)


class Receive(base.CommandAnswering):
    def __init__(self, host):
        super(Receive, self).__init__(
            host,
            "receive",
            use_progress=True,
            use_verbose=True,
            help=_("wait for a file to be sent by a contact"),
        )
        self._overwrite_refused = False  # True when one overwrite as already been refused
        self.action_callbacks = {
            C.META_TYPE_FILE: self.onFileAction,
            C.META_TYPE_OVERWRITE: self.onOverwriteAction,
            C.META_TYPE_NOT_IN_ROSTER_LEAK: self.onNotInRosterAction,
        }

    def add_parser_options(self):
        self.parser.add_argument(
            "jids",
            nargs="*",
            help=_("jids accepted (accept everything if none is specified)"),
        )
        self.parser.add_argument(
            "-m",
            "--multiple",
            action="store_true",
            help=_("accept multiple files (you'll have to stop manually)"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(
                "force overwritting of existing files (/!\\ name is choosed by sender)"
            ),
        )
        self.parser.add_argument(
            "--path",
            default=".",
            metavar="DIR",
            help=_("destination path (default: working directory)"),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("File copy started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("File received successfully"), 2)
        if metadata.get("hash_verified", False):
            try:
                self.disp(
                    _("hash checked: {metadata['hash_algo']}:{metadata['hash']}"), 1
                )
            except KeyError:
                self.disp(_("hash is checked but hash value is missing", 1), error=True)
        else:
            self.disp(_("hash can't be verified"), 1)

    async def onProgressError(self, e):
        self.disp(_("Error while receiving file: {e}").format(e=e), error=True)

    def getXmluiId(self, action_data):
        # FIXME: we temporarily use ElementTree, but a real XMLUI managing module
        #        should be available in the futur
        # TODO: XMLUI module
        try:
            xml_ui = action_data["xmlui"]
        except KeyError:
            self.disp(_("Action has no XMLUI"), 1)
        else:
            ui = ET.fromstring(xml_ui.encode("utf-8"))
            xmlui_id = ui.get("submit")
            if not xmlui_id:
                self.disp(_("Invalid XMLUI received"), error=True)
            return xmlui_id

    async def onFileAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            from_jid = jid.JID(action_data["meta_from_jid"])
        except KeyError:
            self.disp(_("Ignoring action without from_jid data"), 1)
            return
        try:
            progress_id = action_data["meta_progress_id"]
        except KeyError:
            self.disp(_("ignoring action without progress id"), 1)
            return

        if not self.bare_jids or from_jid.bare in self.bare_jids:
            if self._overwrite_refused:
                self.disp(_("File refused because overwrite is needed"), error=True)
                await self.host.bridge.launchAction(
                    xmlui_id, {"cancelled": C.BOOL_TRUE}, profile_key=profile
                )
                return self.host.quitFromSignal(2)
            await self.set_progress_id(progress_id)
            xmlui_data = {"path": self.path}
            await self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)

    async def onOverwriteAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            progress_id = action_data["meta_progress_id"]
        except KeyError:
            self.disp(_("ignoring action without progress id"), 1)
            return
        self.disp(_("Overwriting needed"), 1)

        if progress_id == self.progress_id:
            if self.args.force:
                self.disp(_("Overwrite accepted"), 2)
            else:
                self.disp(_("Refused to overwrite"), 2)
                self._overwrite_refused = True

            xmlui_data = {"answer": C.boolConst(self.args.force)}
            await self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)

    async def onNotInRosterAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            from_jid = jid.JID(action_data["meta_from_jid"])
        except ValueError:
            self.disp(
                _('invalid "from_jid" value received, ignoring: {value}').format(
                    value=from_jid
                ),
                error=True,
            )
            return
        except KeyError:
            self.disp(_('ignoring action without "from_jid" value'), error=True)
            return
        self.disp(_("Confirmation needed for request from an entity not in roster"), 1)

        if from_jid.bare in self.bare_jids:
            # if the sender is expected, we can confirm the session
            confirmed = True
            self.disp(_("Sender confirmed because she or he is explicitly expected"), 1)
        else:
            xmlui = xmlui_manager.create(self.host, action_data["xmlui"])
            confirmed = await self.host.confirm(xmlui.dlg.message)

        xmlui_data = {"answer": C.boolConst(confirmed)}
        await self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)
        if not confirmed and not self.args.multiple:
            self.disp(_("Session refused for {from_jid}").format(from_jid=from_jid))
            self.host.quitFromSignal(0)

    async def start(self):
        self.bare_jids = [jid.JID(jid_).bare for jid_ in self.args.jids]
        self.path = os.path.abspath(self.args.path)
        if not os.path.isdir(self.path):
            self.disp(_("Given path is not a directory !", error=True))
            self.host.quit(C.EXIT_BAD_ARG)
        if self.args.multiple:
            self.host.quit_on_progress_end = False
        self.disp(_("waiting for incoming file request"), 2)
        await self.start_answering()


class Get(base.CommandBase):
    def __init__(self, host):
        super(Get, self).__init__(
            host,
            "get",
            use_progress=True,
            use_verbose=True,
            help=_("download a file from URI"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-o",
            "--dest-file",
            type=str,
            default="",
            help=_("destination file (DEFAULT: filename from URL)"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("overwrite existing file without confirmation"),
        )
        self.parser.add_argument("uri", type=str, help=_("URI of the file to retrieve"))

    async def onProgressStarted(self, metadata):
        self.disp(_("File download started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("File downloaded successfully"), 2)

    async def onProgressError(self, error_msg):
        self.disp(_("Error while downloading file: {}").format(error_msg), error=True)

    async def gotId(self, data):
        """Called when a progress id has been received"""
        try:
            await self.set_progress_id(data["progress"])
        except KeyError:
            if "xmlui" in data:
                ui = xmlui_manager.create(self.host, data["xmlui"])
                await ui.show()
            else:
                self.disp(_("Can't download file"), error=True)
            self.host.quit(C.EXIT_ERROR)

    async def start(self):
        uri = self.args.uri
        dest_file = self.args.dest_file
        if not dest_file:
            parsed_uri = urlparse(uri)
            dest_file = Path(parsed_uri.path).name.strip() or "downloaded_file"

        dest_file = Path(dest_file).expanduser().resolve()
        if dest_file.exists() and not self.args.force:
            message = _("File {path} already exists! Do you want to overwrite?").format(
                path=dest_file
            )
            await self.host.confirmOrQuit(message, _("file download cancelled"))

        options = {}

        try:
            download_data = await self.host.bridge.fileDownload(
                uri,
                str(dest_file),
                data_format.serialise(options),
                self.profile,
            )
        except Exception as e:
            self.disp(f"error while trying to download a file: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.gotId(download_data)


class Upload(base.CommandBase):
    def __init__(self, host):
        super(Upload, self).__init__(
            host, "upload", use_progress=True, use_verbose=True, help=_("upload a file")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-e",
            "--encrypt",
            action="store_true",
            help=_("encrypt file using AES-GCM"),
        )
        self.parser.add_argument("file", type=str, help=_("file to upload"))
        self.parser.add_argument(
            "jid",
            nargs="?",
            help=_("jid of upload component (nothing to autodetect)"),
        )
        self.parser.add_argument(
            "--ignore-tls-errors",
            action="store_true",
            help=_(r"ignore invalide TLS certificate (/!\ Dangerous /!\)"),
        )

    async def onProgressStarted(self, metadata):
        self.disp(_("File upload started"), 2)

    async def onProgressFinished(self, metadata):
        self.disp(_("File uploaded successfully"), 2)
        try:
            url = metadata["url"]
        except KeyError:
            self.disp("download URL not found in metadata")
        else:
            self.disp(_("URL to retrieve the file:"), 1)
            # XXX: url is displayed alone on a line to make parsing easier
            self.disp(url)

    async def onProgressError(self, error_msg):
        self.disp(_("Error while uploading file: {}").format(error_msg), error=True)

    async def gotId(self, data, file_):
        """Called when a progress id has been received

        @param pid(unicode): progress id
        @param file_(str): file path
        """
        try:
            await self.set_progress_id(data["progress"])
        except KeyError:
            if "xmlui" in data:
                ui = xmlui_manager.create(self.host, data["xmlui"])
                await ui.show()
            else:
                self.disp(_("Can't upload file"), error=True)
            self.host.quit(C.EXIT_ERROR)

    async def start(self):
        file_ = self.args.file
        if not os.path.exists(file_):
            self.disp(
                _("file {file_} doesn't exist !").format(file_=repr(file_)), error=True
            )
            self.host.quit(C.EXIT_BAD_ARG)
        if os.path.isdir(file_):
            self.disp(_("{file_} is a dir! Can't upload a dir").format(file_=repr(file_)))
            self.host.quit(C.EXIT_BAD_ARG)

        if self.args.jid is None:
            self.full_dest_jid = ""
        else:
            self.full_dest_jid = await self.host.get_full_jid(self.args.jid)

        options = {}
        if self.args.ignore_tls_errors:
            options["ignore_tls_errors"] = True
        if self.args.encrypt:
            options["encryption"] = C.ENC_AES_GCM

        path = os.path.abspath(file_)
        try:
            upload_data = await self.host.bridge.fileUpload(
                path,
                "",
                self.full_dest_jid,
                data_format.serialise(options),
                self.profile,
            )
        except Exception as e:
            self.disp(f"error while trying to upload a file: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.gotId(upload_data, file_)


class ShareAffiliationsSet(base.CommandBase):
    def __init__(self, host):
        super(ShareAffiliationsSet, self).__init__(
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            help=_("set affiliations for a shared file/directory"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-N",
            "--namespace",
            default="",
            help=_("namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            default="",
            help=_("path to the repository"),
        )
        self.parser.add_argument(
            "-a",
            "--affiliation",
            dest="affiliations",
            metavar=("JID", "AFFILIATION"),
            required=True,
            action="append",
            nargs=2,
            help=_("entity/affiliation couple(s)"),
        )
        self.parser.add_argument(
            "jid",
            help=_("jid of file sharing entity"),
        )

    async def start(self):
        affiliations = dict(self.args.affiliations)
        try:
            affiliations = await self.host.bridge.FISAffiliationsSet(
                self.args.jid,
                self.args.namespace,
                self.args.path,
                affiliations,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set affiliations: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class ShareAffiliationsGet(base.CommandBase):
    def __init__(self, host):
        super(ShareAffiliationsGet, self).__init__(
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            help=_("retrieve affiliations of a shared file/directory"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-N",
            "--namespace",
            default="",
            help=_("namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            default="",
            help=_("path to the repository"),
        )
        self.parser.add_argument(
            "jid",
            help=_("jid of sharing entity"),
        )

    async def start(self):
        try:
            affiliations = await self.host.bridge.FISAffiliationsGet(
                self.args.jid,
                self.args.namespace,
                self.args.path,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get affiliations: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(affiliations)
            self.host.quit()


class ShareAffiliations(base.CommandBase):
    subcommands = (ShareAffiliationsGet, ShareAffiliationsSet)

    def __init__(self, host):
        super(ShareAffiliations, self).__init__(
            host, "affiliations", use_profile=False, help=_("affiliations management")
        )


class ShareConfigurationSet(base.CommandBase):
    def __init__(self, host):
        super(ShareConfigurationSet, self).__init__(
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            help=_("set configuration for a shared file/directory"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-N",
            "--namespace",
            default="",
            help=_("namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            default="",
            help=_("path to the repository"),
        )
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            required=True,
            metavar=("KEY", "VALUE"),
            help=_("configuration field to set (required)"),
        )
        self.parser.add_argument(
            "jid",
            help=_("jid of file sharing entity"),
        )

    async def start(self):
        configuration = dict(self.args.fields)
        try:
            configuration = await self.host.bridge.FISConfigurationSet(
                self.args.jid,
                self.args.namespace,
                self.args.path,
                configuration,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set configuration: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class ShareConfigurationGet(base.CommandBase):
    def __init__(self, host):
        super(ShareConfigurationGet, self).__init__(
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            help=_("retrieve configuration of a shared file/directory"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-N",
            "--namespace",
            default="",
            help=_("namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            default="",
            help=_("path to the repository"),
        )
        self.parser.add_argument(
            "jid",
            help=_("jid of sharing entity"),
        )

    async def start(self):
        try:
            configuration = await self.host.bridge.FISConfigurationGet(
                self.args.jid,
                self.args.namespace,
                self.args.path,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get configuration: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(configuration)
            self.host.quit()


class ShareConfiguration(base.CommandBase):
    subcommands = (ShareConfigurationGet, ShareConfigurationSet)

    def __init__(self, host):
        super(ShareConfiguration, self).__init__(
            host,
            "configuration",
            use_profile=False,
            help=_("file sharing node configuration"),
        )


class ShareList(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(ShareList, self).__init__(
            host,
            "list",
            use_output=C.OUTPUT_LIST_DICT,
            extra_outputs=extra_outputs,
            help=_("retrieve files shared by an entity"),
            use_verbose=True,
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-d",
            "--path",
            default="",
            help=_("path to the directory containing the files"),
        )
        self.parser.add_argument(
            "jid",
            nargs="?",
            default="",
            help=_("jid of sharing entity (nothing to check our own jid)"),
        )

    def _name_filter(self, name, row):
        if row.type == C.FILE_TYPE_DIRECTORY:
            return A.color(C.A_DIRECTORY, name)
        elif row.type == C.FILE_TYPE_FILE:
            return A.color(C.A_FILE, name)
        else:
            self.disp(_("unknown file type: {type}").format(type=row.type), error=True)
            return name

    def _size_filter(self, size, row):
        if not size:
            return ""
        return A.color(A.BOLD, utils.getHumanSize(size))

    def default_output(self, files_data):
        """display files a way similar to ls"""
        files_data.sort(key=lambda d: d["name"].lower())
        show_header = False
        if self.verbosity == 0:
            keys = headers = ("name", "type")
        elif self.verbosity == 1:
            keys = headers = ("name", "type", "size")
        elif self.verbosity > 1:
            show_header = True
            keys = ("name", "type", "size", "file_hash")
            headers = ("name", "type", "size", "hash")
        table = common.Table.fromListDict(
            self.host,
            files_data,
            keys=keys,
            headers=headers,
            filters={"name": self._name_filter, "size": self._size_filter},
            defaults={"size": "", "file_hash": ""},
        )
        table.display_blank(show_header=show_header, hide_cols=["type"])

    async def start(self):
        try:
            files_data = await self.host.bridge.FISList(
                self.args.jid,
                self.args.path,
                {},
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't retrieve shared files: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        await self.output(files_data)
        self.host.quit()


class SharePath(base.CommandBase):
    def __init__(self, host):
        super(SharePath, self).__init__(
            host, "path", help=_("share a file or directory"), use_verbose=True
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help=_("virtual name to use (default: use directory/file name)"),
        )
        perm_group = self.parser.add_mutually_exclusive_group()
        perm_group.add_argument(
            "-j",
            "--jid",
            metavar="JID",
            action="append",
            dest="jids",
            default=[],
            help=_("jid of contacts allowed to retrieve the files"),
        )
        perm_group.add_argument(
            "--public",
            action="store_true",
            help=_(
                r"share publicly the file(s) (/!\ *everybody* will be able to access "
                r"them)"
            ),
        )
        self.parser.add_argument(
            "path",
            help=_("path to a file or directory to share"),
        )

    async def start(self):
        self.path = os.path.abspath(self.args.path)
        if self.args.public:
            access = {"read": {"type": "public"}}
        else:
            jids = self.args.jids
            if jids:
                access = {"read": {"type": "whitelist", "jids": jids}}
            else:
                access = {}
        try:
            name = await self.host.bridge.FISSharePath(
                self.args.name,
                self.path,
                json.dumps(access, ensure_ascii=False),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't share path: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(
                _('{path} shared under the name "{name}"').format(
                    path=self.path, name=name
                )
            )
            self.host.quit()


class ShareInvite(base.CommandBase):
    def __init__(self, host):
        super(ShareInvite, self).__init__(
            host, "invite", help=_("send invitation for a shared repository")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-n",
            "--name",
            default="",
            help=_("name of the repository"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            default="",
            help=_("namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            help=_("path to the repository"),
        )
        self.parser.add_argument(
            "-t",
            "--type",
            choices=["files", "photos"],
            default="files",
            help=_("type of the repository"),
        )
        self.parser.add_argument(
            "-T",
            "--thumbnail",
            help=_("https URL of a image to use as thumbnail"),
        )
        self.parser.add_argument(
            "service",
            help=_("jid of the file sharing service hosting the repository"),
        )
        self.parser.add_argument(
            "jid",
            help=_("jid of the person to invite"),
        )

    async def start(self):
        self.path = os.path.normpath(self.args.path) if self.args.path else ""
        extra = {}
        if self.args.thumbnail is not None:
            if not self.args.thumbnail.startswith("http"):
                self.parser.error(_("only http(s) links are allowed with --thumbnail"))
            else:
                extra["thumb_url"] = self.args.thumbnail
        try:
            await self.host.bridge.FISInvite(
                self.args.jid,
                self.args.service,
                self.args.type,
                self.args.namespace,
                self.path,
                self.args.name,
                data_format.serialise(extra),
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't send invitation: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("invitation sent to {jid}").format(jid=self.args.jid))
            self.host.quit()


class Share(base.CommandBase):
    subcommands = (
        ShareList,
        SharePath,
        ShareInvite,
        ShareAffiliations,
        ShareConfiguration,
    )

    def __init__(self, host):
        super(Share, self).__init__(
            host, "share", use_profile=False, help=_("files sharing management")
        )


class File(base.CommandBase):
    subcommands = (Send, Request, Receive, Get, Upload, Share)

    def __init__(self, host):
        super(File, self).__init__(
            host, "file", use_profile=False, help=_("files sending/receiving/management")
        )
