#!/usr/bin/env python3


# SAT plugin for file tansfer
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
from functools import partial
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools import xml_tools
from sat.tools import stream
from sat.tools import utils
from sat.tools.common import utils as common_utils


log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Tansfer",
    C.PI_IMPORT_NAME: "FILE",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_MAIN: "FilePlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """File Tansfer Management:
This plugin manage the various ways of sending a file, and choose the best one."""
    ),
}


SENDING = D_("Please select a file to send to {peer}")
SENDING_TITLE = D_("File sending")
CONFIRM = D_(
    '{peer} wants to send the file "{name}" to you:\n{desc}\n\nThe file has a size of '
    '{size_human}\n\nDo you accept ?'
)
CONFIRM_TITLE = D_("Confirm file transfer")
CONFIRM_OVERWRITE = D_("File {} already exists, are you sure you want to overwrite ?")
CONFIRM_OVERWRITE_TITLE = D_("File exists")
SECURITY_LIMIT = 30

PROGRESS_ID_KEY = "progress_id"


class FilePlugin:
    File = stream.SatFile

    def __init__(self, host):
        log.info(_("plugin File initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileSend",
            ".plugin",
            in_sign="ssssa{ss}s",
            out_sign="a{ss}",
            method=self._fileSend,
            async_=True,
        )
        self._file_managers = []
        host.importMenu(
            (D_("Action"), D_("send file")),
            self._fileSendMenu,
            security_limit=10,
            help_string=D_("Send a file"),
            type_=C.MENU_SINGLE,
        )

    def _fileSend(self, peer_jid_s, filepath, name="", file_desc="", extra=None,
                  profile=C.PROF_KEY_NONE):
        client = self.host.getClient(profile)
        return defer.ensureDeferred(self.fileSend(
            client, jid.JID(peer_jid_s), filepath, name or None, file_desc or None, extra
        ))

    async def fileSend(
        self, client, peer_jid, filepath, filename=None, file_desc=None, extra=None
    ):
        """Send a file using best available method

        @param peer_jid(jid.JID): jid of the destinee
        @param filepath(str): absolute path to the file
        @param filename(unicode, None): name to use, or None to find it from filepath
        @param file_desc(unicode, None): description of the file
        @param profile: %(doc_profile)s
        @return (dict): action dictionary, with progress id in case of success, else
            xmlui message
        """
        if not os.path.isfile(filepath):
            raise exceptions.DataError("The given path doesn't link to a file")
        if not filename:
            filename = os.path.basename(filepath) or "_"
        for manager, priority in self._file_managers:
            if await utils.asDeferred(manager.canHandleFileSend,
                                      client, peer_jid, filepath):
                try:
                    method_name = manager.name
                except AttributeError:
                    method_name = manager.__class__.__name__
                log.info(
                    _("{name} method will be used to send the file").format(
                        name=method_name
                    )
                )
                try:
                    progress_id = await utils.asDeferred(
                        manager.fileSend, client, peer_jid, filepath, filename, file_desc,
                        extra
                    )
                except Exception as e:
                    log.warning(
                        _("Can't send {filepath} to {peer_jid} with {method_name}: "
                          "{reason}").format(
                              filepath=filepath,
                              peer_jid=peer_jid,
                              method_name=method_name,
                              reason=e
                          )
                    )
                    continue
                return {"progress": progress_id}
        msg = "Can't find any method to send file to {jid}".format(jid=peer_jid.full())
        log.warning(msg)
        return {
            "xmlui": xml_tools.note(
                "Can't transfer file", msg, C.XMLUI_DATA_LVL_WARNING
            ).toXml()
        }

    def _onFileChoosed(self, peer_jid, data, profile):
        client = self.host.getClient(profile)
        cancelled = C.bool(data.get("cancelled", C.BOOL_FALSE))
        if cancelled:
            return
        path = data["path"]
        return self.fileSend(client, peer_jid, path)

    def _fileSendMenu(self, data, profile):
        """ XMLUI activated by menu: return file sending UI

        @param profile: %(doc_profile)s
        """
        try:
            jid_ = jid.JID(data["jid"])
        except RuntimeError:
            raise exceptions.DataError(_("Invalid JID"))

        file_choosed_id = self.host.registerCallback(
            partial(self._onFileChoosed, jid_),
            with_data=True,
            one_shot=True,
        )
        xml_ui = xml_tools.XMLUI(
            C.XMLUI_DIALOG,
            dialog_opt={
                C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_FILE,
                C.XMLUI_DATA_MESS: _(SENDING).format(peer=jid_.full()),
            },
            title=_(SENDING_TITLE),
            submit_id=file_choosed_id,
        )

        return {"xmlui": xml_ui.toXml()}

    def register(self, manager, priority: int = 0) -> None:
        """Register a fileSending manager

        @param manager: object implementing canHandleFileSend, and fileSend methods
        @param priority: pririoty of this manager, the higher available will be used
        """
        m_data = (manager, priority)
        if m_data in self._file_managers:
            raise exceptions.ConflictError(
                f"Manager {manager} is already registered"
            )
        if not hasattr(manager, "canHandleFileSend") or not hasattr(manager, "fileSend"):
            raise ValueError(
                f'{manager} must have both "canHandleFileSend" and "fileSend" methods to '
                'be registered')
        self._file_managers.append(m_data)
        self._file_managers.sort(key=lambda m: m[1], reverse=True)

    def unregister(self, manager):
        for idx, data in enumerate(self._file_managers):
            if data[0] == manager:
                break
        else:
            raise exceptions.NotFound("The file manager {manager} is not registered")
        del self._file_managers[idx]

    # Dialogs with user
    # the overwrite check is done here

    def openFileWrite(self, client, file_path, transfer_data, file_data, stream_object):
        """create SatFile or FileStremaObject for the requested file and fill suitable data
        """
        if stream_object:
            assert "stream_object" not in transfer_data
            transfer_data["stream_object"] = stream.FileStreamObject(
                self.host,
                client,
                file_path,
                mode="wb",
                uid=file_data[PROGRESS_ID_KEY],
                size=file_data["size"],
                data_cb=file_data.get("data_cb"),
            )
        else:
            assert "file_obj" not in transfer_data
            transfer_data["file_obj"] = stream.SatFile(
                self.host,
                client,
                file_path,
                mode="wb",
                uid=file_data[PROGRESS_ID_KEY],
                size=file_data["size"],
                data_cb=file_data.get("data_cb"),
            )

    async def _gotConfirmation(
        self, client, data, peer_jid, transfer_data, file_data, stream_object
    ):
        """Called when the permission and dest path have been received

        @param peer_jid(jid.JID): jid of the file sender
        @param transfer_data(dict): same as for [self.getDestDir]
        @param file_data(dict): same as for [self.getDestDir]
        @param stream_object(bool): same as for [self.getDestDir]
        return (bool): True if copy is wanted and OK
            False if user wants to cancel
            if file exists ask confirmation and call again self._getDestDir if needed
        """
        if data.get("cancelled", False):
            return False
        path = data["path"]
        file_data["file_path"] = file_path = os.path.join(path, file_data["name"])
        log.debug("destination file path set to {}".format(file_path))

        # we manage case where file already exists
        if os.path.exists(file_path):
            overwrite = await xml_tools.deferConfirm(
                self.host,
                _(CONFIRM_OVERWRITE).format(file_path),
                _(CONFIRM_OVERWRITE_TITLE),
                action_extra={
                    "meta_from_jid": peer_jid.full(),
                    "meta_type": C.META_TYPE_OVERWRITE,
                    "meta_progress_id": file_data[PROGRESS_ID_KEY],
                },
                security_limit=SECURITY_LIMIT,
                profile=client.profile,
            )

            if not overwrite:
                return await self.getDestDir(client, peer_jid, transfer_data, file_data)

        self.openFileWrite(client, file_path, transfer_data, file_data, stream_object)
        return True

    async def getDestDir(
        self, client, peer_jid, transfer_data, file_data, stream_object=False
    ):
        """Request confirmation and destination dir to user

        Overwrite confirmation is managed.
        if transfer is confirmed, 'file_obj' is added to transfer_data
        @param peer_jid(jid.JID): jid of the file sender
        @param filename(unicode): name of the file
        @param transfer_data(dict): data of the transfer session,
            it will be only used to store the file_obj.
            "file_obj" (or "stream_object") key *MUST NOT* exist before using getDestDir
        @param file_data(dict): information about the file to be transfered
            It MUST contain the following keys:
                - peer_jid (jid.JID): other peer jid
                - name (unicode): name of the file to trasnsfer
                    the name must not be empty or contain a "/" character
                - size (int): size of the file
                - desc (unicode): description of the file
                - progress_id (unicode): id to use for progression
            It *MUST NOT* contain the "peer" key
            It may contain:
                - data_cb (callable): method called on each data read/write
            "file_path" will be added to this dict once destination selected
            "size_human" will also be added with human readable file size
        @param stream_object(bool): if True, a stream_object will be used instead of file_obj
            a stream.FileStreamObject will be used
        return: True if transfer is accepted
        """
        cont, ret_value = await self.host.trigger.asyncReturnPoint(
            "FILE_getDestDir", client, peer_jid, transfer_data, file_data, stream_object
        )
        if not cont:
            return ret_value
        filename = file_data["name"]
        assert filename and not "/" in filename
        assert PROGRESS_ID_KEY in file_data
        # human readable size
        file_data["size_human"] = common_utils.getHumanSize(file_data["size"])
        resp_data = await xml_tools.deferDialog(
            self.host,
            _(CONFIRM).format(peer=peer_jid.full(), **file_data),
            _(CONFIRM_TITLE),
            type_=C.XMLUI_DIALOG_FILE,
            options={C.XMLUI_DATA_FILETYPE: C.XMLUI_DATA_FILETYPE_DIR},
            action_extra={
                "meta_from_jid": peer_jid.full(),
                "meta_type": C.META_TYPE_FILE,
                "meta_progress_id": file_data[PROGRESS_ID_KEY],
            },
            security_limit=SECURITY_LIMIT,
            profile=client.profile,
        )

        accepted = await self._gotConfirmation(
            client,
            resp_data,
            peer_jid,
            transfer_data,
            file_data,
            stream_object,
        )
        return accepted
