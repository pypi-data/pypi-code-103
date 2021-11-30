#!/usr/bin/env python3

# Libervia File Sharing component
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
import mimetypes
import tempfile
from functools import partial
import shortuuid
import unicodedata
from urllib.parse import urljoin, urlparse, quote, unquote
from pathlib import Path
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools import stream
from sat.tools import video
from sat.tools.common import regex
from sat.tools.common import uri
from sat.tools.common import files_utils
from sat.tools.common import utils
from sat.tools.common import tls
from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import error
from twisted.web import server, resource, static, http
from wokkel import pubsub
from wokkel import generic


log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File sharing component",
    C.PI_IMPORT_NAME: "file-sharing",
    C.PI_MODES: [C.PLUG_MODE_COMPONENT],
    C.PI_TYPE: C.PLUG_TYPE_ENTRY_POINT,
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [
        "FILE",
        "FILE_SHARING_MANAGEMENT",
        "XEP-0106",
        "XEP-0234",
        "XEP-0260",
        "XEP-0261",
        "XEP-0264",
        "XEP-0329",
        "XEP-0363",
    ],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "FileSharing",
    C.PI_HANDLER: C.BOOL_TRUE,
    C.PI_DESCRIPTION: _("""Component hosting and sharing files"""),
}

HASH_ALGO = "sha-256"
NS_COMMENTS = "org.salut-a-toi.comments"
NS_FS_AFFILIATION = "org.salut-a-toi.file-sharing-affiliation"
COMMENT_NODE_PREFIX = "org.salut-a-toi.file_comments/"
# Directory used to buffer request body (i.e. file in case of PUT) we use more than one @
# there, to be sure than it's not conflicting with a JID
TMP_BUFFER_DIR = "@@tmp@@"
OVER_QUOTA_TXT = D_(
    "You are over quota, your maximum allowed size is {quota} and you are already using "
    "{used_space}, you can't upload {file_size} more."
)

server.version = unicodedata.normalize(
    'NFKD',
    f"{C.APP_NAME} file sharing {C.APP_VERSION}"
).encode('ascii','ignore')


class HTTPFileServer(resource.Resource):
    isLeaf = True

    def errorPage(self, request, code):
        request.setResponseCode(code)
        if code == http.BAD_REQUEST:
            brief = 'Bad Request'
            details = "Your request is invalid"
        elif code == http.FORBIDDEN:
            brief = 'Forbidden'
            details = "You're not allowed to use this resource"
        elif code == http.NOT_FOUND:
            brief = 'Not Found'
            details = "No resource found at this URL"
        else:
            brief = 'Error'
            details = "This resource can't be used"
            log.error(f"Unexpected return code used: {code}")
        log.warning(
            f'Error returned while trying to access url {request.uri.decode()}: '
            f'"{brief}" ({code}): {details}'
        )

        return resource.ErrorPage(code, brief, details).render(request)

    def getDispositionType(self, media_type, media_subtype):
        if media_type in ('image', 'video'):
            return 'inline'
        elif media_type == 'application' and media_subtype == 'pdf':
            return 'inline'
        else:
            return 'attachment'

    def render(self, request):
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Access-Control-Allow-Methods", "OPTIONS, HEAD, GET, PUT")
        request.setHeader(
            "Access-Control-Allow-Headers",
            "Content-Type, Range, Xmpp-File-Path, Xmpp-File-No-Http")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader("Accept-Ranges", "bytes")

        request.setHeader(
            "Access-Control-Expose-Headers",
            "Date, Content-Length, Content-Range")
        return super().render(request)

    def render_OPTIONS(self, request):
        request.setResponseCode(http.OK)
        return b""

    def render_GET(self, request):
        try:
            request.upload_data
        except exceptions.DataError:
            return self.errorPage(request, http.NOT_FOUND)

        defer.ensureDeferred(self.renderGet(request))
        return server.NOT_DONE_YET

    async def renderGet(self, request):
        try:
            upload_id, filename = request.upload_data
        except exceptions.DataError:
            request.write(self.errorPage(request, http.FORBIDDEN))
            request.finish()
            return
        found_files = await request.file_sharing.host.memory.getFiles(
            client=None, peer_jid=None, perms_to_check=None, public_id=upload_id)
        if not found_files:
            request.write(self.errorPage(request, http.NOT_FOUND))
            request.finish()
            return
        if len(found_files) > 1:
            log.error(f"more that one files found for public id {upload_id!r}")

        found_file = found_files[0]
        file_path = request.file_sharing.files_path/found_file['file_hash']
        file_res = static.File(file_path)
        file_res.type = f'{found_file["media_type"]}/{found_file["media_subtype"]}'
        file_res.encoding = file_res.contentEncodings.get(Path(found_file['name']).suffix)
        disp_type = self.getDispositionType(
            found_file['media_type'], found_file['media_subtype'])
        # the URL is percent encoded, and not all browsers/tools unquote the file name,
        # thus we add a content disposition header
        request.setHeader(
            'Content-Disposition',
            f"{disp_type}; filename*=UTF-8''{quote(found_file['name'])}"
        )
        # cf. https://xmpp.org/extensions/xep-0363.html#server
        request.setHeader(
            'Content-Security-Policy',
            "default-src 'none'; frame-ancestors 'none';"
        )
        ret = file_res.render(request)
        if ret != server.NOT_DONE_YET:
            # HEAD returns directly the result (while GET use a produced)
            request.write(ret)
            request.finish()

    def render_PUT(self, request):
        defer.ensureDeferred(self.renderPut(request))
        return server.NOT_DONE_YET

    async def renderPut(self, request):
        try:
            client, upload_request = request.upload_request_data
            upload_id, filename = request.upload_data
        except AttributeError:
            request.write(self.errorPage(request, http.BAD_REQUEST))
            request.finish()
            return

        # at this point request is checked and file is buffered, we can store it
        # we close the content here, before registering the file
        request.content.close()
        tmp_file_path = Path(request.content.name)
        request.content = None

        # the 2 following headers are not standard, but useful in the context of file
        # sharing with HTTP Upload: first one allow uploader to specify the path
        # and second one will disable public exposure of the file through HTTP
        path = request.getHeader("Xmpp-File-Path")
        if path:
            path = unquote(path)
        else:
            path =  "/uploads"
        if request.getHeader("Xmpp-File-No-Http") is not None:
            public_id = None
        else:
            public_id = upload_id

        file_data = {
            "name": unquote(upload_request.filename),
            "mime_type": upload_request.content_type,
            "size": upload_request.size,
            "path": path
        }

        await request.file_sharing.registerReceivedFile(
            client, upload_request.from_, file_data, tmp_file_path,
            public_id=public_id,
        )

        request.setResponseCode(http.CREATED)
        request.finish()


class FileSharingRequest(server.Request):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._upload_data = None

    @property
    def upload_data(self):
        """A tuple with upload_id and filename retrieved from requested path"""
        if self._upload_data is not None:
            return self._upload_data

        # self.path is not available if we are early in the request (e.g. when gotLength
        # is called), in which case channel._path must be used. On the other hand, when
        # render_[VERB] is called, only self.path is available
        path = self.channel._path if self.path is None else self.path
        # we normalise the path
        path = urlparse(path.decode()).path
        try:
            __, upload_id, filename = path.split('/')
        except ValueError:
            raise exceptions.DataError("no enought path elements")
        if len(upload_id) < 10:
            raise exceptions.DataError(f"invalid upload ID received for a PUT: {upload_id!r}")

        self._upload_data = (upload_id, filename)
        return self._upload_data

    @property
    def file_sharing(self):
        return self.channel.site.file_sharing

    @property
    def file_tmp_dir(self):
        return self.channel.site.file_tmp_dir

    def refuseRequest(self):
        if self.content is not None:
            self.content.close()
        self.content = open(os.devnull, 'w+b')
        self.channel._respondToBadRequestAndDisconnect()

    def gotLength(self, length):
        if self.channel._command.decode().upper() == 'PUT':
            # for PUT we check early if upload_id is fine, to avoid buffering a file we'll refuse
            # we buffer the file in component's TMP_BUFFER_DIR, so we just have to rename it at the end
            try:
                upload_id, filename = self.upload_data
            except exceptions.DataError as e:
                log.warning(f"Invalid PUT request, we stop here: {e}")
                return self.refuseRequest()
            try:
                client, upload_request, timer = self.file_sharing.expected_uploads.pop(upload_id)
            except KeyError:
                log.warning(f"unknown (expired?) upload ID received for a PUT: {upload_id!r}")
                return self.refuseRequest()

            if not timer.active:
                log.warning(f"upload id {upload_id!r} used for a PUT, but it is expired")
                return self.refuseRequest()

            timer.cancel()

            if upload_request.filename != filename:
                log.warning(
                    f"invalid filename for PUT (upload id: {upload_id!r}, URL: {self.channel._path.decode()}). Original "
                    f"{upload_request.filename!r} doesn't match {filename!r}"
                )
                return self.refuseRequest()

            self.upload_request_data = (client, upload_request)

            file_tmp_path = files_utils.get_unique_name(
                self.file_tmp_dir/upload_id)

            self.content = open(file_tmp_path, 'w+b')
        else:
            return super().gotLength(length)


class FileSharingSite(server.Site):
    requestFactory = FileSharingRequest

    def __init__(self, file_sharing):
        self.file_sharing = file_sharing
        self.file_tmp_dir = file_sharing.host.getLocalPath(
            None, C.FILES_TMP_DIR, TMP_BUFFER_DIR, component=True, profile=False
        )
        for old_file in self.file_tmp_dir.iterdir():
            log.debug(f"purging old buffer file at {old_file}")
            old_file.unlink()
        super().__init__(HTTPFileServer())

    def getContentFile(self, length):
        file_tmp_path = self.file_tmp_dir/shortuuid.uuid()
        return open(file_tmp_path, 'w+b')


class FileSharing:

    def __init__(self, host):
        self.host = host
        self.initialised = False

    def init(self):
        # we init once on first component connection,
        # there is not need to init this plugin if not component use it
        # TODO: this plugin should not be loaded at all if no component uses it
        #   and should be loaded dynamically as soon as a suitable profile is created
        if self.initialised:
            return
        self.initialised = True
        log.info(_("File Sharing initialization"))
        self._f = self.host.plugins["FILE"]
        self._jf = self.host.plugins["XEP-0234"]
        self._h = self.host.plugins["XEP-0300"]
        self._t = self.host.plugins["XEP-0264"]
        self._hu = self.host.plugins["XEP-0363"]
        self._hu.registerHandler(self._onHTTPUpload)
        self.host.trigger.add("FILE_getDestDir", self._getDestDirTrigger)
        self.host.trigger.add(
            "XEP-0234_fileSendingRequest", self._fileSendingRequestTrigger, priority=1000
        )
        self.host.trigger.add("XEP-0234_buildFileElement", self._addFileMetadataElts)
        self.host.trigger.add("XEP-0234_parseFileElement", self._getFileMetadataElts)
        self.host.trigger.add("XEP-0329_compGetFilesFromNode", self._addFileMetadata)
        self.host.trigger.add(
            "XEP-0329_compGetFilesFromNode_build_directory",
            self._addDirectoryMetadataElts)
        self.host.trigger.add(
            "XEP-0329_parseResult_directory",
            self._getDirectoryMetadataElts)
        self.files_path = self.host.getLocalPath(None, C.FILES_DIR, profile=False)
        self.http_port = int(self.host.memory.getConfig(
            'component file-sharing', 'http_upload_port', 8888))
        connection_type = self.host.memory.getConfig(
            'component file-sharing', 'http_upload_connection_type', 'https')
        if connection_type not in ('http', 'https'):
            raise exceptions.ConfigError(
                'bad http_upload_connection_type, you must use one of "http" or "https"'
            )
        self.server = FileSharingSite(self)
        self.expected_uploads = {}
        if connection_type == 'http':
            reactor.listenTCP(self.http_port, self.server)
        else:
            options = tls.getOptionsFromConfig(
                self.host.memory.config, "component file-sharing")
            tls.TLSOptionsCheck(options)
            context_factory = tls.getTLSContextFactory(options)
            reactor.listenSSL(self.http_port, self.server, context_factory)

    def getHandler(self, client):
        return Comments_handler(self)

    def profileConnecting(self, client):
        self.init()
        public_base_url = self.host.memory.getConfig(
            'component file-sharing', 'http_upload_public_facing_url')
        if public_base_url is None:
            client._file_sharing_base_url = f"https://{client.host}:{self.http_port}"
        else:
            client._file_sharing_base_url = public_base_url
        path = client.file_tmp_dir = os.path.join(
            self.host.memory.getConfig("", "local_dir"),
            C.FILES_TMP_DIR,
            regex.pathEscape(client.profile),
        )
        if not os.path.exists(path):
            os.makedirs(path)

    def getQuota(self, client, entity):
        """Return maximum size allowed for all files for entity"""
        # TODO: handle special entities like admins
        quotas = self.host.memory.getConfig("component file-sharing", "quotas_json", {})
        entity_bare_s = entity.userhost()
        try:
            quota = quotas["jids"][entity_bare_s]
        except KeyError:
            quota = quotas.get("users")
        return None if quota is None else utils.parseSize(quota)

    async def generate_thumbnails(self, extra: dict, image_path: Path):
        thumbnails = extra.setdefault(C.KEY_THUMBNAILS, [])
        for max_thumb_size in self._t.SIZES:
            try:
                thumb_size, thumb_id = await self._t.generateThumbnail(
                    image_path,
                    max_thumb_size,
                    #  we keep thumbnails for 6 months
                    60 * 60 * 24 * 31 * 6,
                )
            except Exception as e:
                log.warning(_("Can't create thumbnail: {reason}").format(reason=e))
                break
            thumbnails.append({"id": thumb_id, "size": thumb_size})

    async def registerReceivedFile(
            self, client, peer_jid, file_data, file_path, public_id=None, extra=None):
        """Post file reception tasks

        once file is received, this method create hash/thumbnails if necessary
        move the file to the right location, and create metadata entry in database
        """
        name = file_data["name"]
        if extra is None:
            extra = {}

        mime_type = file_data.get("mime_type")
        if not mime_type or mime_type == "application/octet-stream":
            mime_type = mimetypes.guess_type(name)[0]

        is_image = mime_type is not None and mime_type.startswith("image")
        is_video = mime_type is not None and mime_type.startswith("video")

        if file_data.get("hash_algo") == HASH_ALGO:
            log.debug(_("Reusing already generated hash"))
            file_hash = file_data["hash_hasher"].hexdigest()
        else:
            hasher = self._h.getHasher(HASH_ALGO)
            with file_path.open('rb') as f:
                file_hash = await self._h.calculateHash(f, hasher)
        final_path = self.files_path/file_hash

        if final_path.is_file():
            log.debug(
                "file [{file_hash}] already exists, we can remove temporary one".format(
                    file_hash=file_hash
                )
            )
            file_path.unlink()
        else:
            file_path.rename(final_path)
            log.debug(
                "file [{file_hash}] moved to {files_path}".format(
                    file_hash=file_hash, files_path=self.files_path
                )
            )

        if is_image:
            await self.generate_thumbnails(extra, final_path)
        elif is_video:
            with tempfile.TemporaryDirectory() as tmp_dir:
                thumb_path = Path(tmp_dir) / "thumbnail.jpg"
                try:
                    await video.get_thumbnail(final_path, thumb_path)
                except Exception as e:
                    log.warning(_("Can't get thumbnail for {final_path}: {e}").format(
                        final_path=final_path, e=e))
                else:
                    await self.generate_thumbnails(extra, thumb_path)

        self.host.memory.setFile(
            client,
            name=name,
            version="",
            file_hash=file_hash,
            hash_algo=HASH_ALGO,
            size=file_data["size"],
            path=file_data.get("path"),
            namespace=file_data.get("namespace"),
            mime_type=mime_type,
            public_id=public_id,
            owner=peer_jid,
            extra=extra,
        )

    async def _getDestDirTrigger(
        self, client, peer_jid, transfer_data, file_data, stream_object
    ):
        """This trigger accept file sending request, and store file locally"""
        if not client.is_component:
            return True, None
        # client._file_sharing_allowed_hosts is set in plugin XEP-0329
        if peer_jid.host not in client._file_sharing_allowed_hosts:
            raise error.StanzaError("forbidden")
        assert stream_object
        assert "stream_object" not in transfer_data
        assert C.KEY_PROGRESS_ID in file_data
        filename = file_data["name"]
        assert filename and not "/" in filename
        quota = self.getQuota(client, peer_jid)
        if quota is not None:
            used_space = await self.host.memory.fileGetUsedSpace(client, peer_jid)

            if (used_space + file_data["size"]) > quota:
                raise error.StanzaError(
                    "not-acceptable",
                    text=OVER_QUOTA_TXT.format(
                        quota=utils.getHumanSize(quota),
                        used_space=utils.getHumanSize(used_space),
                        file_size=utils.getHumanSize(file_data['size'])
                    )
                )
        file_tmp_dir = self.host.getLocalPath(
            None, C.FILES_TMP_DIR, peer_jid.userhost(), component=True, profile=False
        )
        file_tmp_path = file_data['file_path'] = files_utils.get_unique_name(
            file_tmp_dir/filename)

        transfer_data["finished_d"].addCallback(
            lambda __: defer.ensureDeferred(
                self.registerReceivedFile(client, peer_jid, file_data, file_tmp_path)
            )
        )

        self._f.openFileWrite(
            client, file_tmp_path, transfer_data, file_data, stream_object
        )
        return False, True

    @defer.inlineCallbacks
    def _retrieveFiles(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """This method retrieve a file on request, and send if after checking permissions"""
        peer_jid = session["peer_jid"]
        if session['local_jid'].user:
            owner = client.getOwnerFromJid(session['local_jid'])
        else:
            owner = peer_jid
        try:
            found_files = yield self.host.memory.getFiles(
                client,
                peer_jid=peer_jid,
                name=file_data.get("name"),
                file_hash=file_data.get("file_hash"),
                hash_algo=file_data.get("hash_algo"),
                path=file_data.get("path"),
                namespace=file_data.get("namespace"),
                owner=owner,
            )
        except exceptions.NotFound:
            found_files = None
        except exceptions.PermissionError:
            log.warning(
                _("{peer_jid} is trying to access an unauthorized file: {name}").format(
                    peer_jid=peer_jid, name=file_data.get("name")
                )
            )
            defer.returnValue(False)

        if not found_files:
            log.warning(
                _("no matching file found ({file_data})").format(file_data=file_data)
            )
            defer.returnValue(False)

        # we only use the first found file
        found_file = found_files[0]
        if found_file['type'] != C.FILE_TYPE_FILE:
            raise TypeError("a file was expected, type is {type_}".format(
                type_=found_file['type']))
        file_hash = found_file["file_hash"]
        file_path = self.files_path / file_hash
        file_data["hash_hasher"] = hasher = self._h.getHasher(found_file["hash_algo"])
        size = file_data["size"] = found_file["size"]
        file_data["file_hash"] = file_hash
        file_data["hash_algo"] = found_file["hash_algo"]

        # we complete file_elt so peer can have some details on the file
        if "name" not in file_data:
            file_elt.addElement("name", content=found_file["name"])
        file_elt.addElement("size", content=str(size))
        content_data["stream_object"] = stream.FileStreamObject(
            self.host,
            client,
            file_path,
            uid=self._jf.getProgressId(session, content_name),
            size=size,
            data_cb=lambda data: hasher.update(data),
        )
        defer.returnValue(True)

    def _fileSendingRequestTrigger(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        if not client.is_component:
            return True, None
        else:
            return (
                False,
                self._retrieveFiles(
                    client, session, content_data, content_name, file_data, file_elt
                ),
            )

    ## HTTP Upload ##

    def _purge_slot(self, upload_id):
        try:
            del self.expected_uploads[upload_id]
        except KeyError:
            log.error(f"trying to purge an inexisting upload slot ({upload_id})")

    async def _onHTTPUpload(self, client, request):
        # filename should be already cleaned, but it's better to double check
        assert '/' not in request.filename
        # client._file_sharing_allowed_hosts is set in plugin XEP-0329
        if request.from_.host not in client._file_sharing_allowed_hosts:
            raise error.StanzaError("forbidden")

        quota = self.getQuota(client, request.from_)
        if quota is not None:
            used_space = await self.host.memory.fileGetUsedSpace(client, request.from_)

            if (used_space + request.size) > quota:
                raise error.StanzaError(
                    "not-acceptable",
                    text=OVER_QUOTA_TXT.format(
                        quota=utils.getHumanSize(quota),
                        used_space=utils.getHumanSize(used_space),
                        file_size=utils.getHumanSize(request.size)
                    ),
                    appCondition = self._hu.getFileTooLargeElt(max(quota - used_space, 0))
                )

        upload_id = shortuuid.ShortUUID().random(length=30)
        assert '/' not in upload_id
        timer = reactor.callLater(30, self._purge_slot, upload_id)
        self.expected_uploads[upload_id] = (client, request, timer)
        url = urljoin(client._file_sharing_base_url, f"{upload_id}/{request.filename}")
        slot = self._hu.Slot(
            put=url,
            get=url,
            headers=[],
        )
        return slot

    ## metadata triggers ##

    def _addFileMetadataElts(self, client, file_elt, extra_args):
        # affiliation
        affiliation = extra_args.get('affiliation')
        if affiliation is not None:
            file_elt.addElement((NS_FS_AFFILIATION, "affiliation"), content=affiliation)

        # comments
        try:
            comments_url = extra_args.pop("comments_url")
        except KeyError:
            return

        comment_elt = file_elt.addElement((NS_COMMENTS, "comments"), content=comments_url)

        try:
            count = len(extra_args["extra"]["comments"])
        except KeyError:
            count = 0

        comment_elt["count"] = str(count)
        return True

    def _getFileMetadataElts(self, client, file_elt, file_data):
        # affiliation
        try:
            affiliation_elt = next(file_elt.elements(NS_FS_AFFILIATION, "affiliation"))
        except StopIteration:
            pass
        else:
            file_data["affiliation"] = str(affiliation_elt)

        # comments
        try:
            comments_elt = next(file_elt.elements(NS_COMMENTS, "comments"))
        except StopIteration:
            pass
        else:
            file_data["comments_url"] = str(comments_elt)
            file_data["comments_count"] = comments_elt["count"]
        return True

    def _addFileMetadata(
            self, client, iq_elt, iq_result_elt, owner, node_path, files_data):
        for file_data in files_data:
            file_data["comments_url"] = uri.buildXMPPUri(
                "pubsub",
                path=client.jid.full(),
                node=COMMENT_NODE_PREFIX + file_data["id"],
            )
        return True

    def _addDirectoryMetadataElts(
            self, client, file_data, directory_elt, owner, node_path):
        affiliation = file_data.get('affiliation')
        if affiliation is not None:
            directory_elt.addElement(
                (NS_FS_AFFILIATION, "affiliation"),
                content=affiliation
            )

    def _getDirectoryMetadataElts(
            self, client, elt, file_data):
        try:
            affiliation_elt = next(elt.elements((NS_FS_AFFILIATION, "affiliation")))
        except StopIteration:
            pass
        else:
            file_data['affiliation'] = str(affiliation_elt)


class Comments_handler(pubsub.PubSubService):
    """This class is a minimal Pubsub service handling virtual nodes for comments"""

    def __init__(self, plugin_parent):
        super(Comments_handler, self).__init__()
        self.host = plugin_parent.host
        self.plugin_parent = plugin_parent
        self.discoIdentity = {
            "category": "pubsub",
            "type": "virtual",  # FIXME: non standard, here to avoid this service being considered as main pubsub one
            "name": "files commenting service",
        }

    def _getFileId(self, nodeIdentifier):
        if not nodeIdentifier.startswith(COMMENT_NODE_PREFIX):
            raise error.StanzaError("item-not-found")
        file_id = nodeIdentifier[len(COMMENT_NODE_PREFIX) :]
        if not file_id:
            raise error.StanzaError("item-not-found")
        return file_id

    @defer.inlineCallbacks
    def getFileData(self, requestor, nodeIdentifier):
        file_id = self._getFileId(nodeIdentifier)
        try:
            files = yield self.host.memory.getFiles(self.parent, requestor, file_id)
        except (exceptions.NotFound, exceptions.PermissionError):
            # we don't differenciate between NotFound and PermissionError
            # to avoid leaking information on existing files
            raise error.StanzaError("item-not-found")
        if not files:
            raise error.StanzaError("item-not-found")
        if len(files) > 1:
            raise error.InternalError("there should be only one file")
        defer.returnValue(files[0])

    def commentsUpdate(self, extra, new_comments, peer_jid):
        """update comments (replace or insert new_comments)

        @param extra(dict): extra data to update
        @param new_comments(list[tuple(unicode, unicode, unicode)]): comments to update or insert
        @param peer_jid(unicode, None): bare jid of the requestor, or None if request is done by owner
        """
        current_comments = extra.setdefault("comments", [])
        new_comments_by_id = {c[0]: c for c in new_comments}
        updated = []
        # we now check every current comment, to see if one id in new ones
        # exist, in which case we must update
        for idx, comment in enumerate(current_comments):
            comment_id = comment[0]
            if comment_id in new_comments_by_id:
                # a new comment has an existing id, update is requested
                if peer_jid and comment[1] != peer_jid:
                    # requestor has not the right to modify the comment
                    raise exceptions.PermissionError
                # we replace old_comment with updated one
                new_comment = new_comments_by_id[comment_id]
                current_comments[idx] = new_comment
                updated.append(new_comment)

        # we now remove every updated comments, to only keep
        # the ones to insert
        for comment in updated:
            new_comments.remove(comment)

        current_comments.extend(new_comments)

    def commentsDelete(self, extra, comments):
        try:
            comments_dict = extra["comments"]
        except KeyError:
            return
        for comment in comments:
            try:
                comments_dict.remove(comment)
            except ValueError:
                continue

    def _getFrom(self, item_elt):
        """retrieve published of an item

        @param item_elt(domish.element): <item> element
        @return (unicode): full jid as string
        """
        iq_elt = item_elt
        while iq_elt.parent != None:
            iq_elt = iq_elt.parent
        return iq_elt["from"]

    @defer.inlineCallbacks
    def publish(self, requestor, service, nodeIdentifier, items):
        #  we retrieve file a first time to check authorisations
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        file_id = file_data["id"]
        comments = [(item["id"], self._getFrom(item), item.toXml()) for item in items]
        if requestor.userhostJID() == file_data["owner"]:
            peer_jid = None
        else:
            peer_jid = requestor.userhost()
        update_cb = partial(self.commentsUpdate, new_comments=comments, peer_jid=peer_jid)
        try:
            yield self.host.memory.fileUpdate(file_id, "extra", update_cb)
        except exceptions.PermissionError:
            raise error.StanzaError("not-authorized")

    @defer.inlineCallbacks
    def items(self, requestor, service, nodeIdentifier, maxItems, itemIdentifiers):
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        comments = file_data["extra"].get("comments", [])
        if itemIdentifiers:
            defer.returnValue(
                [generic.parseXml(c[2]) for c in comments if c[0] in itemIdentifiers]
            )
        else:
            defer.returnValue([generic.parseXml(c[2]) for c in comments])

    @defer.inlineCallbacks
    def retract(self, requestor, service, nodeIdentifier, itemIdentifiers):
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        file_id = file_data["id"]
        try:
            comments = file_data["extra"]["comments"]
        except KeyError:
            raise error.StanzaError("item-not-found")

        to_remove = []
        for comment in comments:
            comment_id = comment[0]
            if comment_id in itemIdentifiers:
                to_remove.append(comment)
                itemIdentifiers.remove(comment_id)
                if not itemIdentifiers:
                    break

        if itemIdentifiers:
            # not all items have been to_remove, we can't continue
            raise error.StanzaError("item-not-found")

        if requestor.userhostJID() != file_data["owner"]:
            if not all([c[1] == requestor.userhost() for c in to_remove]):
                raise error.StanzaError("not-authorized")

        remove_cb = partial(self.commentsDelete, comments=to_remove)
        yield self.host.memory.fileUpdate(file_id, "extra", remove_cb)
