#!/usr/bin/env python3

# SàT plugin for HTTP File Upload (XEP-0363)
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

import os.path
import mimetypes
from typing import NamedTuple, Callable, Optional
from dataclasses import dataclass
from urllib import parse
from wokkel import disco, iwokkel
from zope.interface import implementer
from twisted.words.protocols.jabber import jid, xmlstream, error
from twisted.words.xish import domish
from twisted.internet import reactor
from twisted.internet import defer
from twisted.web import client as http_client
from twisted.web import http_headers
from sat.core.i18n import _
from sat.core.xmpp import SatXMPPComponent
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools import web as sat_web, utils


log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "HTTP File Upload",
    C.PI_IMPORT_NAME: "XEP-0363",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0363"],
    C.PI_DEPENDENCIES: ["FILE", "UPLOAD"],
    C.PI_MAIN: "XEP_0363",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of HTTP File Upload"""),
}

NS_HTTP_UPLOAD = "urn:xmpp:http:upload:0"
IQ_HTTP_UPLOAD_REQUEST = C.IQ_GET + '/request[@xmlns="' + NS_HTTP_UPLOAD + '"]'
ALLOWED_HEADERS = ('authorization', 'cookie', 'expires')


@dataclass
class Slot:
    """Upload slot"""
    put: str
    get: str
    headers: list


class UploadRequest(NamedTuple):
    from_: jid.JID
    filename: str
    size: int
    content_type: Optional[str]


class RequestHandler(NamedTuple):
    callback: Callable[[SatXMPPComponent, UploadRequest], Optional[Slot]]
    priority: int


class XEP_0363:
    Slot=Slot

    def __init__(self, host):
        log.info(_("plugin HTTP File Upload initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileHTTPUpload",
            ".plugin",
            in_sign="sssbs",
            out_sign="",
            method=self._fileHTTPUpload,
        )
        host.bridge.addMethod(
            "fileHTTPUploadGetSlot",
            ".plugin",
            in_sign="sisss",
            out_sign="(ssaa{ss})",
            method=self._getSlot,
            async_=True,
        )
        host.plugins["UPLOAD"].register(
            "HTTP Upload", self.getHTTPUploadEntity, self.fileHTTPUpload
        )
        # list of callbacks used when a request is done to a component
        self.handlers = []
        # XXX: there is not yet official short name, so we use "http_upload"
        host.registerNamespace("http_upload", NS_HTTP_UPLOAD)

    def getHandler(self, client):
        return XEP_0363_handler(self)

    def registerHandler(self, callback, priority=0):
        """Register a request handler

        @param callack: method to call when a request is done
            the callback must return a Slot if the request is handled,
            otherwise, other callbacks will be tried.
            If the callback raises a StanzaError, its condition will be used if no other
            callback can handle the request.
        @param priority: handlers with higher priorities will be called first
        """
        assert callback not in self.handlers
        req_handler = RequestHandler(callback, priority)
        self.handlers.append(req_handler)
        self.handlers.sort(key=lambda handler: handler.priority, reverse=True)

    def getFileTooLargeElt(self, max_size: int) -> domish.Element:
        """Generate <file-too-large> app condition for errors"""
        file_too_large_elt = domish.Element((NS_HTTP_UPLOAD, "file-too-large"))
        file_too_large_elt.addElement("max-file-size", str(max_size))
        return file_too_large_elt

    async def getHTTPUploadEntity(self, client, upload_jid=None):
        """Get HTTP upload capable entity

         upload_jid is checked, then its components
         @param upload_jid(None, jid.JID): entity to check
         @return(D(jid.JID)): first HTTP upload capable entity
         @raise exceptions.NotFound: no entity found
         """
        try:
            entity = client.http_upload_service
        except AttributeError:
            found_entities = await self.host.findFeaturesSet(client, (NS_HTTP_UPLOAD,))
            try:
                entity = client.http_upload_service = next(iter(found_entities))
            except StopIteration:
                entity = client.http_upload_service = None

        if entity is None:
            raise exceptions.NotFound("No HTTP upload entity found")

        return entity

    def _fileHTTPUpload(self, filepath, filename="", upload_jid="",
                        ignore_tls_errors=False, profile=C.PROF_KEY_NONE):
        assert os.path.isabs(filepath) and os.path.isfile(filepath)
        client = self.host.getClient(profile)
        progress_id_d, __ = defer.ensureDeferred(self.fileHTTPUpload(
            client,
            filepath,
            filename or None,
            jid.JID(upload_jid) if upload_jid else None,
            {"ignore_tls_errors": ignore_tls_errors},
        ))
        return progress_id_d

    async def fileHTTPUpload(
        self, client, filepath, filename=None, upload_jid=None, options=None):
        """Upload a file through HTTP

        @param filepath(str): absolute path of the file
        @param filename(None, unicode): name to use for the upload
            None to use basename of the path
        @param upload_jid(jid.JID, None): upload capable entity jid,
            or None to use autodetected, if possible
        @param options(dict): options where key can be:
            - ignore_tls_errors(bool): if True, SSL certificate will not be checked
        @param profile: %(doc_profile)s
        @return (D(tuple[D(unicode), D(unicode)])): progress id and Deferred which fire
            download URL
        """
        if options is None:
            options = {}
        ignore_tls_errors = options.get("ignore_tls_errors", False)
        filename = filename or os.path.basename(filepath)
        size = os.path.getsize(filepath)

        size_adjust = []
        #: this trigger can be used to modify the requested size, it is notably useful
        #: with encryption. The size_adjust is a list which can be filled by int to add
        #: to the initial size
        self.host.trigger.point(
            "XEP-0363_upload_size", client, options, filepath, size, size_adjust,
            triggers_no_cancel=True)
        if size_adjust:
            size = sum([size, *size_adjust])
        try:
            slot = await self.getSlot(client, filename, size, upload_jid=upload_jid)
        except Exception as e:
            log.warning(_("Can't get upload slot: {reason}").format(reason=e))
            raise e
        else:
            log.debug(f"Got upload slot: {slot}")
            sat_file = self.host.plugins["FILE"].File(
                self.host, client, filepath, uid=options.get("progress_id"), size=size,
                auto_end_signals=False
            )
            progress_id = sat_file.uid

            file_producer = http_client.FileBodyProducer(sat_file)

            if ignore_tls_errors:
                agent = http_client.Agent(reactor, sat_web.NoCheckContextFactory())
            else:
                agent = http_client.Agent(reactor)

            headers = {"User-Agent": [C.APP_NAME.encode("utf-8")]}

            for name, value in slot.headers:
                name = name.encode('utf-8')
                value = value.encode('utf-8')
                headers[name] = value


            await self.host.trigger.asyncPoint(
                "XEP-0363_upload", client, options, sat_file, file_producer, slot,
                triggers_no_cancel=True)

            download_d = agent.request(
                b"PUT",
                slot.put.encode("utf-8"),
                http_headers.Headers(headers),
                file_producer,
            )
            download_d.addCallbacks(
                self._uploadCb,
                self._uploadEb,
                (sat_file, slot),
                None,
                (sat_file,),
            )

            return progress_id, download_d

    def _uploadCb(self, __, sat_file, slot):
        """Called once file is successfully uploaded

        @param sat_file(SatFile): file used for the upload
            should be closed, but it is needed to send the progressFinished signal
        @param slot(Slot): put/get urls
        """
        log.info(f"HTTP upload finished ({slot.get})")
        sat_file.progressFinished({"url": slot.get})
        return slot.get

    def _uploadEb(self, failure_, sat_file):
        """Called on unsuccessful upload

        @param sat_file(SatFile): file used for the upload
            should be closed, be is needed to send the progressError signal
        """
        try:
            wrapped_fail = failure_.value.reasons[0]
        except (AttributeError, IndexError) as e:
            log.warning(_("upload failed: {reason}").format(reason=e))
            sat_file.progressError(str(failure_))
        else:
            if wrapped_fail.check(sat_web.SSLError):
                msg = "TLS validation error, can't connect to HTTPS server"
            else:
                msg = "can't upload file"
            log.warning(msg + ": " + str(wrapped_fail.value))
            sat_file.progressError(msg)
        raise failure_

    def _getSlot(self, filename, size, content_type, upload_jid,
                 profile_key=C.PROF_KEY_NONE):
        """Get an upload slot

        This method can be used when uploading is done by the frontend
        @param filename(unicode): name of the file to upload
        @param size(int): size of the file (must be non null)
        @param upload_jid(str, ''): HTTP upload capable entity
        @param content_type(unicode, None): MIME type of the content
            empty string or None to guess automatically
        """
        client = self.host.getClient(profile_key)
        filename = filename.replace("/", "_")
        d = defer.ensureDeferred(self.getSlot(
            client, filename, size, content_type or None, jid.JID(upload_jid) or None
        ))
        d.addCallback(lambda slot: (slot.get, slot.put, slot.headers))
        return d

    async def getSlot(self, client, filename, size, content_type=None, upload_jid=None):
        """Get a slot (i.e. download/upload links)

        @param filename(unicode): name to use for the upload
        @param size(int): size of the file to upload (must be >0)
        @param content_type(None, unicode): MIME type of the content
            None to autodetect
        @param upload_jid(jid.JID, None): HTTP upload capable upload_jid
            or None to use the server component (if any)
        @param client: %(doc_client)s
        @return (Slot): the upload (put) and download (get) URLs
        @raise exceptions.NotFound: no HTTP upload capable upload_jid has been found
        """
        assert filename and size
        if content_type is None:
            # TODO: manage python magic for file guessing (in a dedicated plugin ?)
            content_type = mimetypes.guess_type(filename, strict=False)[0]

        if upload_jid is None:
            try:
                upload_jid = client.http_upload_service
            except AttributeError:
                found_entity = await self.getHTTPUploadEntity(client)
                return await self.getSlot(
                    client, filename, size, content_type, found_entity)
            else:
                if upload_jid is None:
                    raise exceptions.NotFound("No HTTP upload entity found")

        iq_elt = client.IQ("get")
        iq_elt["to"] = upload_jid.full()
        request_elt = iq_elt.addElement((NS_HTTP_UPLOAD, "request"))
        request_elt["filename"] = filename
        request_elt["size"] = str(size)
        if content_type is not None:
            request_elt["content-type"] = content_type

        iq_result_elt = await iq_elt.send()

        try:
            slot_elt = next(iq_result_elt.elements(NS_HTTP_UPLOAD, "slot"))
            put_elt = next(slot_elt.elements(NS_HTTP_UPLOAD, "put"))
            put_url = put_elt['url']
            get_elt = next(slot_elt.elements(NS_HTTP_UPLOAD, "get"))
            get_url = get_elt['url']
        except (StopIteration, KeyError):
            raise exceptions.DataError("Incorrect stanza received from server")

        headers = []
        for header_elt in put_elt.elements(NS_HTTP_UPLOAD, "header"):
            try:
                name = header_elt["name"]
                value = str(header_elt)
            except KeyError:
                log.warning(_("Invalid header element: {xml}").format(
                    iq_result_elt.toXml()))
                continue
            name = name.replace('\n', '')
            value = value.replace('\n', '')
            if name.lower() not in ALLOWED_HEADERS:
                log.warning(_('Ignoring unauthorised header "{name}": {xml}')
                    .format(name=name, xml = iq_result_elt.toXml()))
                continue
            headers.append((name, value))

        return Slot(put=put_url, get=get_url, headers=headers)

    # component

    def onComponentRequest(self, iq_elt, client):
        iq_elt.handled=True
        defer.ensureDeferred(self.handleComponentRequest(client, iq_elt))

    async def handleComponentRequest(self, client, iq_elt):
        try:
            request_elt = next(iq_elt.elements(NS_HTTP_UPLOAD, "request"))
            request = UploadRequest(
                from_=jid.JID(iq_elt['from']),
                filename=parse.quote(request_elt['filename'].replace('/', '_'), safe=''),
                size=int(request_elt['size']),
                content_type=request_elt.getAttribute('content-type')
            )
        except (StopIteration, KeyError, ValueError):
            client.sendError(iq_elt, "bad-request")
            return

        err = None

        for handler in self.handlers:
            try:
                slot = await utils.asDeferred(handler.callback, client, request)
            except error.StanzaError as e:
                log.warning(
                    "a stanza error has been raised while processing HTTP Upload of "
                    f"request: {e}"
                )
                if err is None:
                    # we keep the first error to return its condition later,
                    # if no other callback handle the request
                    err = e
            else:
                if slot:
                    break
        else:
            log.warning(
                _("no service can handle HTTP Upload request: {elt}")
                .format(elt=iq_elt.toXml()))
            if err is None:
                err = error.StanzaError("feature-not-implemented")
            client.send(err.toResponse(iq_elt))
            return

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        slot_elt = iq_result_elt.addElement((NS_HTTP_UPLOAD, 'slot'))
        put_elt = slot_elt.addElement('put')
        put_elt['url'] = slot.put
        get_elt = slot_elt.addElement('get')
        get_elt['url'] = slot.get
        client.send(iq_result_elt)


@implementer(iwokkel.IDisco)
class XEP_0363_handler(xmlstream.XMPPHandler):

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        if self.parent.is_component:
            self.xmlstream.addObserver(
                IQ_HTTP_UPLOAD_REQUEST, self.plugin_parent.onComponentRequest,
                client=self.parent
            )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_HTTP_UPLOAD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
