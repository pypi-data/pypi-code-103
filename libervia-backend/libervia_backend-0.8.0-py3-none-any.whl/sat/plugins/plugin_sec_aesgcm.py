#!/usr/bin/env python3

# SàT plugin for handling AES-GCM file encryption
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

import re
from textwrap import dedent
from functools import partial
from urllib import parse
import mimetypes
import secrets
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat import backends
from cryptography.exceptions import AlreadyFinalized
import treq
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.tools import stream
from sat.core.log import getLogger
from sat.tools.web import treq_client_no_ssl

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "AES-GCM",
    C.PI_IMPORT_NAME: "AES-GCM",
    C.PI_TYPE: "SEC",
    C.PI_PROTOCOLS: ["OMEMO Media sharing"],
    C.PI_DEPENDENCIES: ["XEP-0363", "XEP-0384", "DOWNLOAD", "ATTACH"],
    C.PI_MAIN: "AESGCM",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: dedent(_("""\
    Implementation of AES-GCM scheme, a way to encrypt files (not official XMPP standard).
    See https://xmpp.org/extensions/inbox/omemo-media-sharing.html for details
    """)),
}

AESGCM_RE = re.compile(
    r'aesgcm:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9'
    r'()@:%_\+.~#?&\/\/=]*)')


class AESGCM(object):

    def __init__(self, host):
        self.host = host
        log.info(_("AESGCM plugin initialization"))
        self._http_upload = host.plugins['XEP-0363']
        self._attach = host.plugins["ATTACH"]
        host.plugins["DOWNLOAD"].registerScheme(
            "aesgcm", self.download
        )
        self._attach.register(
            self.canHandleAttachment, self.attach, encrypted=True)
        host.trigger.add("XEP-0363_upload_size", self._uploadSizeTrigger)
        host.trigger.add("XEP-0363_upload", self._uploadTrigger)
        host.trigger.add("messageReceived", self._messageReceivedTrigger)

    async def download(self, client, uri_parsed, dest_path, options):
        fragment = bytes.fromhex(uri_parsed.fragment)

        # legacy method use 16 bits IV, but OMEMO media sharing published spec indicates
        # which is 12 bits IV (AES-GCM spec recommandation), so we have to determine
        # which size has been used.
        if len(fragment) == 48:
            iv_size = 16
        elif len(fragment) == 44:
            iv_size = 12
        else:
            raise ValueError(
                f"Invalid URL fragment, can't decrypt file at {uri_parsed.get_url()}")

        iv, key = fragment[:iv_size], fragment[iv_size:]

        decryptor = ciphers.Cipher(
            ciphers.algorithms.AES(key),
            modes.GCM(iv),
            backend=backends.default_backend(),
        ).decryptor()

        download_url = parse.urlunparse(
            ('https', uri_parsed.netloc, uri_parsed.path, '', '', ''))

        if options.get('ignore_tls_errors', False):
            log.warning(
                "TLS certificate check disabled, this is highly insecure"
            )
            treq_client = treq_client_no_ssl
        else:
            treq_client = treq

        head_data = await treq_client.head(download_url)
        content_length = int(head_data.headers.getRawHeaders('content-length')[0])
        # the 128 bits tag is put at the end
        file_size = content_length - 16

        file_obj = stream.SatFile(
            self.host,
            client,
            dest_path,
            mode="wb",
            size = file_size,
        )

        progress_id = file_obj.uid

        resp = await treq_client.get(download_url, unbuffered=True)
        if resp.code == 200:
            d = treq.collect(resp, partial(
                self.onDataDownload,
                client=client,
                file_obj=file_obj,
                decryptor=decryptor))
        else:
            d = defer.Deferred()
            self.host.plugins["DOWNLOAD"].errbackDownload(file_obj, d, resp)
        return progress_id, d

    async def canHandleAttachment(self, client, data):
        try:
            await self._http_upload.getHTTPUploadEntity(client)
        except exceptions.NotFound:
            return False
        else:
            return True

    async def _uploadCb(self, client, filepath, filename, options):
        options['encryption'] = C.ENC_AES_GCM
        return await self._http_upload.fileHTTPUpload(
            client=client,
            filepath=filepath,
            filename=filename,
            options=options
        )

    async def attach(self, client, data):
        # XXX: the attachment removal/resend code below is due to the one file per
        #   message limitation of OMEMO media sharing unofficial XEP. We have to remove
        #   attachments from original message, and send them one by one.
        # TODO: this is to be removed when a better mechanism is available with OMEMO (now
        #   possible with the 0.4 version of OMEMO, it's possible to encrypt other stanza
        #   elements than body).
        attachments = data["extra"][C.MESS_KEY_ATTACHMENTS]
        if not data['message'] or data['message'] == {'': ''}:
            extra_attachments = attachments[1:]
            del attachments[1:]
            await self._attach.uploadFiles(client, data, upload_cb=self._uploadCb)
        else:
            # we have a message, we must send first attachment separately
            extra_attachments = attachments[:]
            attachments.clear()
            del data["extra"][C.MESS_KEY_ATTACHMENTS]

        body_elt = next(data["xml"].elements((C.NS_CLIENT, "body")))

        for attachment in attachments:
            body_elt.addContent(attachment["url"])

        for attachment in extra_attachments:
            # we send all remaining attachment in a separate message
            await client.sendMessage(
                to_jid=data['to'],
                message={'': ''},
                subject=data['subject'],
                mess_type=data['type'],
                extra={C.MESS_KEY_ATTACHMENTS: [attachment]},
            )

        if ((not data['extra']
             and (not data['message'] or data['message'] == {'': ''})
             and not data['subject'])):
            # nothing left to send, we can cancel the message
            raise exceptions.CancelError("Cancelled by AESGCM attachment handling")

    def onDataDownload(self, data, client, file_obj, decryptor):
        if file_obj.tell() + len(data) > file_obj.size:
            # we're reaching end of file with this bunch of data
            # we may still have a last bunch if the tag is incomplete
            bytes_left = file_obj.size - file_obj.tell()
            if bytes_left > 0:
                decrypted = decryptor.update(data[:bytes_left])
                file_obj.write(decrypted)
                tag = data[bytes_left:]
            else:
                tag = data
            if len(tag) < 16:
                # the tag is incomplete, either we'll get the rest in next data bunch
                # or we have already the other part from last bunch of data
                try:
                    # we store partial tag in decryptor._sat_tag
                    tag = decryptor._sat_tag + tag
                except AttributeError:
                    # no other part, we'll get the rest at next bunch
                    decryptor.sat_tag = tag
                else:
                    # we have the complete tag, it must be 128 bits
                    if len(tag) != 16:
                        raise ValueError(f"Invalid tag: {tag}")
            remain = decryptor.finalize_with_tag(tag)
            file_obj.write(remain)
            file_obj.close()
        else:
            decrypted = decryptor.update(data)
            file_obj.write(decrypted)

    def _uploadSizeTrigger(self, client, options, file_path, size, size_adjust):
        if options.get('encryption') != C.ENC_AES_GCM:
            return True
        # the tag is appended to the file
        size_adjust.append(16)
        return True

    def _encrypt(self, data, encryptor):
        if data:
            return encryptor.update(data)
        else:
            try:
                # end of file is reached, me must finalize
                ret = encryptor.finalize()
                tag = encryptor.tag
                return ret + tag
            except AlreadyFinalized:
                # as we have already finalized, we can now send EOF
                return b''

    def _uploadTrigger(self, client, options, sat_file, file_producer, slot):
        if options.get('encryption') != C.ENC_AES_GCM:
            return True
        log.debug("encrypting file with AES-GCM")
        iv = secrets.token_bytes(12)
        key = secrets.token_bytes(32)
        fragment = f'{iv.hex()}{key.hex()}'
        ori_url = parse.urlparse(slot.get)
        # we change the get URL with the one with aesgcm scheme and containing the
        # encoded key + iv
        slot.get = parse.urlunparse(['aesgcm', *ori_url[1:5], fragment])

        # encrypted data size will be bigger than original file size
        # so we need to check with final data length to avoid a warning on close()
        sat_file.check_size_with_read = True

        # file_producer get length directly from file, and this cause trouble has
        # we have to change the size because of encryption. So we adapt it here,
        # else the producer would stop reading prematurely
        file_producer.length = sat_file.size

        encryptor = ciphers.Cipher(
            ciphers.algorithms.AES(key),
            modes.GCM(iv),
            backend=backends.default_backend(),
        ).encryptor()

        if sat_file.data_cb is not None:
            raise exceptions.InternalError(
                f"data_cb was expected to be None, it is set to {sat_file.data_cb}")

        # with data_cb we encrypt the file on the fly
        sat_file.data_cb = partial(self._encrypt, encryptor=encryptor)
        return True


    def _popAESGCMLinks(self, match, links):
        link = match.group()
        if link not in links:
            links.append(link)
        return ""

    def _checkAESGCMAttachments(self, client, data):
        if not data.get('message'):
            return data
        links = []

        for lang, message in list(data['message'].items()):
            message = AESGCM_RE.sub(
                partial(self._popAESGCMLinks, links=links),
                message)
            if links:
                message = message.strip()
                if not message:
                    del data['message'][lang]
                else:
                    data['message'][lang] = message
                mess_encrypted = client.encryption.isEncrypted(data)
                attachments = data['extra'].setdefault(C.MESS_KEY_ATTACHMENTS, [])
                for link in links:
                    path = parse.urlparse(link).path
                    attachment = {
                        "url": link,
                    }
                    media_type = mimetypes.guess_type(path, strict=False)[0]
                    if media_type is not None:
                        attachment[C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE] = media_type

                    if mess_encrypted:
                        # we don't add the encrypted flag if the message itself is not
                        # encrypted, because the decryption key is part of the link,
                        # so sending it over unencrypted channel is like having no
                        # encryption at all.
                        attachment['encrypted'] = True
                    attachments.append(attachment)

        return data

    def _messageReceivedTrigger(self, client, message_elt, post_treat):
        # we use a post_treat callback instead of "message_parse" trigger because we need
        # to check if the "encrypted" flag is set to decide if we add the same flag to the
        # attachment
        post_treat.addCallback(partial(self._checkAESGCMAttachments, client))
        return True
