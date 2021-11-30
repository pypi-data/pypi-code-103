#!/usr/bin/env python3

# SAT plugin for uploading files
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
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.tools.common import data_format
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools import xml_tools

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Upload",
    C.PI_IMPORT_NAME: "UPLOAD",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_MAIN: "UploadPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""File upload management"""),
}


UPLOADING = D_("Please select a file to upload")
UPLOADING_TITLE = D_("File upload")


class UploadPlugin(object):
    # TODO: plugin unload

    def __init__(self, host):
        log.info(_("plugin Upload initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileUpload",
            ".plugin",
            in_sign="sssss",
            out_sign="a{ss}",
            method=self._fileUpload,
            async_=True,
        )
        self._upload_callbacks = []

    def _fileUpload(
        self, filepath, filename, upload_jid_s="", options='', profile=C.PROF_KEY_NONE
    ):
        client = self.host.getClient(profile)
        upload_jid = jid.JID(upload_jid_s) if upload_jid_s else None
        options = data_format.deserialise(options)

        return defer.ensureDeferred(self.fileUpload(
            client, filepath, filename or None, upload_jid, options
        ))

    async def fileUpload(self, client, filepath, filename, upload_jid, options):
        """Send a file using best available method

        parameters are the same as for [upload]
        @return (dict): action dictionary, with progress id in case of success, else xmlui
            message
        """
        try:
            progress_id, __ = await self.upload(
                client, filepath, filename, upload_jid, options)
        except Exception as e:
            if (isinstance(e, jabber_error.StanzaError)
                and e.condition == 'not-acceptable'):
                reason = e.text
            else:
                reason = str(e)
            msg = D_("Can't upload file: {reason}").format(reason=reason)
            log.warning(msg)
            return {
                "xmlui": xml_tools.note(
                    msg, D_("Can't upload file"), C.XMLUI_DATA_LVL_WARNING
                ).toXml()
            }
        else:
            return {"progress": progress_id}

    async def upload(self, client, filepath, filename=None, upload_jid=None,
                     options=None):
        """Send a file using best available method

        @param filepath(str): absolute path to the file
        @param filename(None, unicode): name to use for the upload
            None to use basename of the path
        @param upload_jid(jid.JID, None): upload capable entity jid,
            or None to use autodetected, if possible
        @param options(dict): option to use for the upload, may be:
            - ignore_tls_errors(bool): True to ignore SSL/TLS certificate verification
                used only if HTTPS transport is needed
            - progress_id(str): id to use for progression
                if not specified, one will be generated
        @param profile: %(doc_profile)s
        @return (tuple[unicode,D(unicode)]): progress_id and a Deferred which fire
            download URL when upload is finished
        """
        if options is None:
            options = {}
        if not os.path.isfile(filepath):
            raise exceptions.DataError("The given path doesn't link to a file")
        for method_name, available_cb, upload_cb, priority in self._upload_callbacks:
            if upload_jid is None:
                try:
                    upload_jid = await available_cb(client, upload_jid)
                except exceptions.NotFound:
                    continue  # no entity managing this extension found

            log.info(
                "{name} method will be used to upload the file".format(name=method_name)
            )
            progress_id, download_d = await upload_cb(
                client, filepath, filename, upload_jid, options
            )
            return progress_id, download_d

        raise exceptions.NotFound("Can't find any method to upload a file")

    def register(self, method_name, available_cb, upload_cb, priority=0):
        """Register a fileUploading method

        @param method_name(unicode): short name for the method, must be unique
        @param available_cb(callable): method to call to check if this method is usable
           the callback must take two arguments: upload_jid (can be None) and profile
           the callback must return the first entity found (being upload_jid or one of its
           components)
           exceptions.NotFound must be raised if no entity has been found
        @param upload_cb(callable): method to upload a file
            must have the same signature as [fileUpload]
            must return a tuple with progress_id and a Deferred which fire download URL
            when upload is finished
        @param priority(int): pririoty of this method, the higher available will be used
        """
        assert method_name
        for data in self._upload_callbacks:
            if method_name == data[0]:
                raise exceptions.ConflictError(
                    "A method with this name is already registered"
                )
        self._upload_callbacks.append((method_name, available_cb, upload_cb, priority))
        self._upload_callbacks.sort(key=lambda data: data[3], reverse=True)

    def unregister(self, method_name):
        for idx, data in enumerate(self._upload_callbacks):
            if data[0] == method_name:
                del [idx]
                return
        raise exceptions.NotFound("The name to unregister doesn't exist")
