#!/usr/bin/env python3

# Libervia: an XMPP client
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

""" interfaces """

import uuid
import os
from zope import interface
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.protocols import basic
from twisted.internet import interfaces

log = getLogger(__name__)


class IStreamProducer(interface.Interface):
    def startStream(consumer):
        """start producing the stream

        @return (D): deferred fired when stream is finished
        """
        pass


class SatFile:
    """A file-like object to have high level files manipulation"""

    # TODO: manage "with" statement

    def __init__(self, host, client, path, mode="rb", uid=None, size=None, data_cb=None,
                 auto_end_signals=True, check_size_with_read=False):
        """
        @param host: %(doc_host)s
        @param path(Path, str): path to the file to get or write to
        @param mode(str): same as for built-in "open" function
        @param uid(unicode, None): unique id identifing this progressing element
            This uid will be used with self.host.progressGet
            will be automaticaly generated if None
        @param size(None, int): size of the file (when known in advance)
        @param data_cb(None, callable): method to call on each data read/write
            can be used to do processing like calculating hash.
            if data_cb return a non None value, it will be used instead of the
            data read/to write
        @param auto_end_signals(bool): if True, progressFinished and progressError signals
            are automatically sent.
            if False, you'll have to call self.progressFinished and self.progressError
            yourself.
            progressStarted signal is always sent automatically
        @param check_size_with_read(bool): if True, size well be checked using number of
            bytes read or written. This is useful when data_cb modifiy len of file.
        """
        self.host = host
        self.profile = client.profile
        self.uid = uid or str(uuid.uuid4())
        self._file = open(path, mode)
        self.size = size
        self.data_cb = data_cb
        self.auto_end_signals = auto_end_signals
        metadata = self.getProgressMetadata()
        self.host.registerProgressCb(
            self.uid, self.getProgress, metadata, profile=client.profile
        )
        self.host.bridge.progressStarted(self.uid, metadata, client.profile)

        self._transfer_count = 0 if check_size_with_read else None

    @property
    def check_size_with_read(self):
        return self._transfer_count is not None

    @check_size_with_read.setter
    def check_size_with_read(self, value):
        if value and self._transfer_count is None:
            self._transfer_count = 0
        else:
            self._transfer_count = None

    def checkSize(self):
        """Check that current size correspond to given size

        must be used when the transfer is supposed to be finished
        @return (bool): True if the position is the same as given size
        @raise exceptions.NotFound: size has not be specified
        """
        if self.check_size_with_read:
            position = self._transfer_count
        else:
            position = self._file.tell()
        if self.size is None:
            raise exceptions.NotFound
        return position == self.size

    def close(self, progress_metadata=None, error=None):
        """Close the current file

        @param progress_metadata(None, dict): metadata to send with _onProgressFinished
            message
        @param error(None, unicode): set to an error message if progress was not
            successful
            mutually exclusive with progress_metadata
            error can happen even if error is None, if current size differ from given size
        """
        if self._file.closed:
            return  # avoid double close (which is allowed) error
        if error is None:
            try:
                size_ok = self.checkSize()
            except exceptions.NotFound:
                size_ok = True
            if not size_ok:
                error = "declared and actual size mismatch"
                log.warning(error)
                progress_metadata = None

        self._file.close()

        if self.auto_end_signals:
            if error is None:
                self.progressFinished(progress_metadata)
            else:
                assert progress_metadata is None
                self.progressError(error)

        self.host.removeProgressCb(self.uid, self.profile)

    @property
    def closed(self):
        return self._file.closed

    def progressFinished(self, metadata=None):
        if metadata is None:
            metadata = {}
        self.host.bridge.progressFinished(self.uid, metadata, self.profile)

    def progressError(self, error):
        self.host.bridge.progressError(self.uid, error, self.profile)

    def flush(self):
        self._file.flush()

    def write(self, buf):
        if self.data_cb is not None:
            ret = self.data_cb(buf)
            if ret is not None:
                buf = ret
        if self._transfer_count is not None:
            self._transfer_count += len(buf)
        self._file.write(buf)

    def read(self, size=-1):
        read = self._file.read(size)
        if self.data_cb is not None:
            ret = self.data_cb(read)
            if ret is not None:
                read = ret
        if self._transfer_count is not None:
            self._transfer_count += len(read)
        return read

    def seek(self, offset, whence=os.SEEK_SET):
        self._file.seek(offset, whence)

    def tell(self):
        return self._file.tell()

    def mode(self):
        return self._file.mode()

    def getProgressMetadata(self):
        """Return progression metadata as given to progressStarted

        @return (dict): metadata (check bridge for documentation)
        """
        metadata = {"type": C.META_TYPE_FILE}

        mode = self._file.mode
        if "+" in mode:
            pass  # we have no direction in read/write modes
        elif mode in ("r", "rb"):
            metadata["direction"] = "out"
        elif mode in ("w", "wb"):
            metadata["direction"] = "in"
        elif "U" in mode:
            metadata["direction"] = "out"
        else:
            raise exceptions.InternalError

        metadata["name"] = self._file.name

        return metadata

    def getProgress(self, progress_id, profile):
        ret = {"position": self._file.tell()}
        if self.size:
            ret["size"] = self.size
        return ret


@interface.implementer(IStreamProducer)
@interface.implementer(interfaces.IConsumer)
class FileStreamObject(basic.FileSender):
    def __init__(self, host, client, path, **kwargs):
        """

        A SatFile will be created and put in self.file_obj
        @param path(unicode): path to the file
        @param **kwargs: kw arguments to pass to SatFile
        """
        self.file_obj = SatFile(host, client, path, **kwargs)

    def registerProducer(self, producer, streaming):
        pass

    def startStream(self, consumer):
        return self.beginFileTransfer(self.file_obj, consumer)

    def write(self, data):
        self.file_obj.write(data)

    def close(self, *args, **kwargs):
        self.file_obj.close(*args, **kwargs)
