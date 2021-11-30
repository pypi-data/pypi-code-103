#!/usr/bin/env python3

# SàT plugin for attaching files
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

from pathlib import Path
from collections import namedtuple
from twisted.internet import defer
import mimetypes
import tempfile
import shutil
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.tools import utils
from sat.tools import image


log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Attach",
    C.PI_IMPORT_NAME: "ATTACH",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_DEPENDENCIES: ["UPLOAD"],
    C.PI_MAIN: "AttachPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Attachments handler"""),
}


AttachmentHandler = namedtuple('AttachmentHandler', ['can_handle', 'attach', 'priority'])


class AttachPlugin:

    def __init__(self, host):
        log.info(_("plugin Attach initialization"))
        self.host = host
        self._u = host.plugins["UPLOAD"]
        host.trigger.add("sendMessage", self._sendMessageTrigger)
        self._attachments_handlers = {'clear': [], 'encrypted': []}
        self.register(self.defaultCanHandle, self.defaultAttach, False, -1000)

    def register(self, can_handle, attach, encrypted=False, priority=0):
        """Register an attachments handler

        @param can_handle(callable, coroutine, Deferred): a method which must return True
            if this plugin can handle the upload, otherwise next ones will be tried.
            This method will get client and mess_data as arguments, before the XML is
            generated
        @param attach(callable, coroutine, Deferred): attach the file
            this method will get client and mess_data as arguments, after XML is
            generated. Upload operation must be handled
            hint: "UPLOAD" plugin can be used
        @param encrypted(bool): True if the handler manages encrypted files
            A handler can be registered twice if it handle both encrypted and clear
            attachments
        @param priority(int): priority of this handler, handler with higher priority will
            be tried first
        """
        handler = AttachmentHandler(can_handle, attach, priority)
        handlers = (
            self._attachments_handlers['encrypted']
            if encrypted else self._attachments_handlers['clear']
        )
        if handler in handlers:
            raise exceptions.InternalError(
                'Attachment handler has been registered twice, this should never happen'
            )

        handlers.append(handler)
        handlers.sort(key=lambda h: h.priority, reverse=True)
        log.debug(f"new attachments handler: {handler}")

    async def attachFiles(self, client, data):
        """Main method to attach file

        It will do generic pre-treatment, and call the suitable attachments handler
        """
        # we check attachment for pre-treatment like large image resizing
        # media_type will be added if missing (and if it can be guessed from path)
        attachments = data["extra"][C.MESS_KEY_ATTACHMENTS]
        tmp_dirs_to_clean = []
        for attachment in attachments:
            if attachment.get(C.MESS_KEY_ATTACHMENTS_RESIZE, False):
                path = Path(attachment["path"])
                try:
                    media_type = attachment[C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE]
                except KeyError:
                    media_type = mimetypes.guess_type(path, strict=False)[0]
                    if media_type is None:
                        log.warning(
                            _("Can't resize attachment of unknown type: {attachment}")
                            .format(attachment=attachment))
                        continue
                    attachment[C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE] = media_type

                main_type = media_type.split('/')[0]
                if main_type == "image":
                    report = image.check(self.host, path)
                    if report['too_large']:
                        tmp_dir = Path(tempfile.mkdtemp())
                        tmp_dirs_to_clean.append(tmp_dir)
                        new_path = tmp_dir / path.name
                        await image.resize(
                            path, report["recommended_size"], dest=new_path)
                        attachment["path"] = new_path
                        log.info(
                            _("Attachment {path!r} has been resized at {new_path!r}")
                            .format(path=str(path), new_path=str(new_path)))
                else:
                    log.warning(
                        _("Can't resize attachment of type {main_type!r}: {attachment}")
                        .format(main_type=main_type, attachment=attachment))

        if client.encryption.isEncryptionRequested(data):
            handlers = self._attachments_handlers['encrypted']
        else:
            handlers = self._attachments_handlers['clear']

        for handler in handlers:
            can_handle = await utils.asDeferred(handler.can_handle, client, data)
            if can_handle:
                break
        else:
            raise exceptions.NotFound(
                _("No plugin can handle attachment with {destinee}").format(
                destinee = data['to']
            ))

        await utils.asDeferred(handler.attach, client, data)

        for dir_path in tmp_dirs_to_clean:
            log.debug(f"Cleaning temporary directory at {dir_path}")
            shutil.rmtree(dir_path)

        return data

    async def uploadFiles(self, client, data, upload_cb=None):
        """Upload file, and update attachments

        invalid attachments will be removed
        @param client:
        @param data(dict): message data
        @param upload_cb(coroutine, Deferred, None): method to use for upload
            if None, upload method from UPLOAD plugin will be used.
            Otherwise, following kwargs will be use with the cb:
                - client
                - filepath
                - filename
                - options
            the method must return a tuple similar to UPLOAD plugin's upload method,
            it must contain:
                - progress_id
                - a deferred which fire download URL
        """
        if upload_cb is None:
            upload_cb = self._u.upload

        uploads_d = []
        to_delete = []
        attachments = data["extra"]["attachments"]

        for attachment in attachments:
            try:
                # we pop path because we don't want it to be stored, as the image can be
                # only in a temporary location
                path = Path(attachment.pop("path"))
            except KeyError:
                log.warning("no path in attachment: {attachment}")
                to_delete.append(attachment)
                continue

            if "url" in attachment:
                url = attachment.pop('url')
                log.warning(
                    f"unexpected URL in attachment: {url!r}\nattachment: {attachment}"
                )

            try:
                name = attachment["name"]
            except KeyError:
                name = attachment["name"] = path.name

            options = {}
            progress_id = attachment.pop("progress_id", None)
            if progress_id:
                options["progress_id"] = progress_id
            check_certificate = self.host.memory.getParamA(
                "check_certificate", "Connection", profile_key=client.profile)
            if not check_certificate:
                options['ignore_tls_errors'] = True
                log.warning(
                    _("certificate check disabled for upload, this is dangerous!"))

            __, upload_d = await upload_cb(
                client=client,
                filepath=path,
                filename=name,
                options=options,
            )
            uploads_d.append(upload_d)

        for attachment in to_delete:
            attachments.remove(attachment)

        upload_results = await defer.DeferredList(uploads_d)
        for idx, (success, ret) in enumerate(upload_results):
            attachment = attachments[idx]

            if not success:
                # ret is a failure here
                log.warning(f"error while uploading {attachment}: {ret}")
                continue

            attachment["url"] = ret

        return data

    def _attachFiles(self, data, client):
        return defer.ensureDeferred(self.attachFiles(client, data))

    def _sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments):
        if mess_data['extra'].get(C.MESS_KEY_ATTACHMENTS):
            post_xml_treatments.addCallback(self._attachFiles, client=client)
        return True

    async def defaultCanHandle(self, client, data):
        return True

    async def defaultAttach(self, client, data):
        await self.uploadFiles(client, data)
        # TODO: handle xhtml-im
        body_elt = next(data["xml"].elements((C.NS_CLIENT, "body")))
        attachments = data["extra"][C.MESS_KEY_ATTACHMENTS]
        if attachments:
            body_links = '\n'.join(a['url'] for a in attachments)
            if str(body_elt).strip():
                # if there is already a body, we add a line feed before the first link
                body_elt.addContent('\n')
            body_elt.addContent(body_links)
