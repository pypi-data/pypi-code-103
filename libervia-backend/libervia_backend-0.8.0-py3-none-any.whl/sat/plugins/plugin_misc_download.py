#!/usr/bin/env python3

# SAT plugin for downloading files
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
from urllib.parse import urlparse, unquote
import hashlib
import treq
from twisted.internet import defer
from twisted.words.protocols.jabber import error as jabber_error
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools import xml_tools
from sat.tools.common import data_format
from sat.tools import stream
from sat.tools.web import treq_client_no_ssl

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Download",
    C.PI_IMPORT_NAME: "DOWNLOAD",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MAIN: "DownloadPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""File download management"""),
}


class DownloadPlugin(object):

    def __init__(self, host):
        log.info(_("plugin Download initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileDownload",
            ".plugin",
            in_sign="ssss",
            out_sign="a{ss}",
            method=self._fileDownload,
            async_=True,
        )
        host.bridge.addMethod(
            "fileDownloadComplete",
            ".plugin",
            in_sign="ssss",
            out_sign="s",
            method=self._fileDownloadComplete,
            async_=True,
        )
        self._download_callbacks = {}
        self.registerScheme('http', self.downloadHTTP)
        self.registerScheme('https', self.downloadHTTP)

    def _fileDownload(self, uri, dest_path, options_s, profile):
        client = self.host.getClient(profile)
        options = data_format.deserialise(options_s)

        return defer.ensureDeferred(self.fileDownload(
            client, uri, Path(dest_path), options
        ))

    async def fileDownload(self, client, uri, dest_path, options=None):
        """Download a file using best available method

        parameters are the same as for [download]
        @return (dict): action dictionary, with progress id in case of success, else xmlui
            message
        """
        try:
            progress_id, __ = await self.download(client, uri, dest_path, options)
        except Exception as e:
            if (isinstance(e, jabber_error.StanzaError)
                and e.condition == 'not-acceptable'):
                reason = e.text
            else:
                reason = str(e)
            msg = D_("Can't download file: {reason}").format(reason=reason)
            log.warning(msg)
            return {
                "xmlui": xml_tools.note(
                    msg, D_("Can't download file"), C.XMLUI_DATA_LVL_WARNING
                ).toXml()
            }
        else:
            return {"progress": progress_id}

    def _fileDownloadComplete(self, uri, dest_path, options_s, profile):
        client = self.host.getClient(profile)
        options = data_format.deserialise(options_s)

        d = defer.ensureDeferred(self.fileDownloadComplete(
            client, uri, dest_path, options
        ))
        d.addCallback(lambda path: str(path))
        return d

    async def fileDownloadComplete(self, client, uri, dest_path, options=None):
        """Helper method to fully download a file and return its path

        parameters are the same as for [download]
        @return (str): path to the downloaded file
            use empty string to store the file in cache
        """
        __, download_d = await self.download(client, uri, dest_path, options)
        dest_path = await download_d
        return dest_path

    async def download(self, client, uri, dest_path, options=None):
        """Send a file using best available method

        @param uri(str): URI to the file to download
        @param dest_path(str, Path): where the file must be downloaded
            if empty string, the file will be stored in local path
        @param options(dict, None): options depending on scheme handler
            Some common options:
                - ignore_tls_errors(bool): True to ignore SSL/TLS certificate verification
                  used only if HTTPS transport is needed
        @return (tuple[unicode,D(unicode)]): progress_id and a Deferred which fire
            download URL when download is finished
            progress_id can be empty string if the file already exist and is not
            downloaded again (can happen if cache is used with empty dest_path)
        """
        if options is None:
            options = {}

        uri_parsed = urlparse(uri, 'http')
        if dest_path:
            dest_path = Path(dest_path)
            cache_uid = None
        else:
            filename = Path(unquote(uri_parsed.path)).name.strip() or C.FILE_DEFAULT_NAME
            # we don't use Path.suffixes because we don't want to have more than 2
            # suffixes, but we still want to handle suffixes like "tar.gz".
            stem, *suffixes = filename.rsplit('.', 2)
            # we hash the URL to have an unique identifier, and avoid double download
            url_hash = hashlib.sha256(uri_parsed.geturl().encode()).hexdigest()
            cache_uid = f"{stem}_{url_hash}"
            cache_data = client.cache.getMetadata(cache_uid)
            if cache_data is not None:
                # file is already in cache, we return it
                download_d = defer.succeed(cache_data['path'])
                return '', download_d
            else:
                # the file is not in cache
                unique_name = '.'.join([cache_uid] + suffixes)
                with client.cache.cacheData(
                    "DOWNLOAD", cache_uid, filename=unique_name) as f:
                    # we close the file and only use its name, the file will be opened
                    # by the registered callback
                    dest_path = Path(f.name)

        # should we check certificates?
        check_certificate = self.host.memory.getParamA(
            "check_certificate", "Connection", profile_key=client.profile)
        if not check_certificate:
            options['ignore_tls_errors'] = True
            log.warning(
                _("certificate check disabled for download, this is dangerous!"))

        try:
            callback = self._download_callbacks[uri_parsed.scheme]
        except KeyError:
            raise exceptions.NotFound(f"Can't find any handler for uri {uri}")
        else:
            try:
                progress_id, download_d = await callback(
                    client, uri_parsed, dest_path, options)
            except Exception as e:
                log.warning(_(
                    "Can't download URI {uri}: {reason}").format(
                    uri=uri, reason=e))
                if cache_uid is not None:
                    client.cache.removeFromCache(cache_uid)
                elif dest_path.exists():
                    dest_path.unlink()
                raise e
            download_d.addCallback(lambda __: dest_path)
            return progress_id, download_d

    def registerScheme(self, scheme, download_cb):
        """Register an URI scheme handler

        @param scheme(unicode): URI scheme this callback is handling
        @param download_cb(callable): callback to download a file
            arguments are:
                - (SatXMPPClient) client
                - (urllib.parse.SplitResult) parsed URI
                - (Path) destination path where the file must be downloaded
                - (dict) options
            must return a tuple with progress_id and a Deferred which fire when download
            is finished
        """
        if scheme in self._download_callbacks:
            raise exceptions.ConflictError(
                f"A method with scheme {scheme!r} is already registered"
            )
        self._download_callbacks[scheme] = download_cb

    def unregister(self, scheme):
        try:
            del self._download_callbacks[scheme]
        except KeyError:
            raise exceptions.NotFound(f"No callback registered for scheme {scheme!r}")

    def errbackDownload(self, file_obj, download_d, resp):
        """Set file_obj and download deferred appropriatly after a network error

        @param file_obj(SatFile): file where the download must be done
        @param download_d(Deferred): deffered which must be fired on complete download
        @param resp(treq.response.IResponse): treq response
        """
        msg = f"HTTP error ({resp.code}): {resp.phrase.decode()}"
        file_obj.close(error=msg)
        download_d.errback(exceptions.NetworkError(msg))

    async def downloadHTTP(self, client, uri_parsed, dest_path, options):
        url = uri_parsed.geturl()

        if options.get('ignore_tls_errors', False):
            log.warning(
                "TLS certificate check disabled, this is highly insecure"
            )
            treq_client = treq_client_no_ssl
        else:
            treq_client = treq

        head_data = await treq_client.head(url)
        try:
            content_length = int(head_data.headers.getRawHeaders('content-length')[0])
        except (KeyError, TypeError, IndexError):
            content_length = None
            log.debug(f"No content lenght found at {url}")
        file_obj = stream.SatFile(
            self.host,
            client,
            dest_path,
            mode="wb",
            size = content_length,
        )

        progress_id = file_obj.uid

        resp = await treq_client.get(url, unbuffered=True)
        if resp.code == 200:
            d = treq.collect(resp, file_obj.write)
            d.addBoth(lambda _: file_obj.close())
        else:
            d = defer.Deferred()
            self.errbackDownload(file_obj, d, resp)
        return progress_id, d
