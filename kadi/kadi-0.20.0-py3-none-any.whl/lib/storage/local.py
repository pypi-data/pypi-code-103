# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import hashlib
import json
import os

import magic
from defusedxml.ElementTree import parse
from flask import current_app

import kadi.lib.constants as const
from .core import BaseStorage
from kadi.lib.exceptions import KadiChecksumMismatchError
from kadi.lib.exceptions import KadiFilesizeExceededError
from kadi.lib.exceptions import KadiFilesizeMismatchError
from kadi.lib.format import filesize
from kadi.lib.utils import get_truth


class LocalStorage(BaseStorage):
    """Storage provider that uses the local file system.

    :param root_directory: The directory the storage operates in. The path must be an
        absolute path.
    :param max_size: (optional) See :class:`.BaseStorage`.
    :param buffer_size: (optional) The buffer size in bytes to use in memory when
        reading files.
    :param dir_len: (optional) Length of each directory.
    :param num_dirs: (optional) Number of directories.
    """

    def __init__(
        self,
        root_directory,
        max_size=None,
        buffer_size=const.ONE_MIB,
        dir_len=2,
        num_dirs=3,
    ):
        super().__init__("local", "chunked", max_size=max_size)

        if not os.path.isabs(root_directory):
            raise ValueError(
                f"Root directory '{root_directory}' is not an absolute path."
            )

        self.buffer_size = buffer_size
        self.dir_len = dir_len
        self.num_dirs = num_dirs
        self._root_directory = os.path.realpath(root_directory)

    @staticmethod
    def filepath_from_name(filename, dir_len=2, num_dirs=3):
        r"""Create a path from a filename.

        Splits up a filename ``"abcdefg"`` into the file path ``"ab/cd/ef/g"``, assuming
        default argument values. Useful to avoid storing lots of files in the same
        directory.

        :param filename: The name of the file.
        :param dir_len: (optional) Length of each directory.
        :param num_dirs: (optional) Number of directories.
        :return: The file path or the original filename, if its length is smaller than
            or equals ``dir_len`` \* ``num_dirs``.
        """
        if dir_len < 1 or num_dirs < 1 or len(filename) <= dir_len * num_dirs:
            return filename

        dirs = [filename[i : i + dir_len] for i in range(0, len(filename), dir_len)]
        filepath = os.path.join(*dirs[0:num_dirs], filename[num_dirs * dir_len :])

        return filepath

    def remove_empty_parent_dirs(self, path, num_dirs=1):
        """Remove empty parent directories given a file name.

        Especially useful in tandem with :meth:`filepath_from_name` to remove unneeded
        directories.

        :param path: The file name to use as base.
        :param num_dirs: (optional) The maximum number of parent directories to remove.
        """
        iteration = 0
        current_dir = os.path.dirname(self._make_absolute(path))

        while (
            # Path is a directory
            os.path.isdir(current_dir)
            # Path must be a subdirectory of the root directory.
            and self._is_subdirectory_of_root(current_dir)
            # Do not delete the root directory.
            and not os.path.samefile(self.root_directory, current_dir)
            # Directory should be empty.
            and not os.listdir(current_dir)
        ):
            if iteration >= num_dirs:
                break

            try:
                os.rmdir(current_dir)
                current_dir = os.path.dirname(current_dir)
                iteration += 1
            except OSError:
                break

    def exists(self, filepath):
        """Check if a file exists.

        :param filepath: The local storage path of the file.
        :return: ``True`` if the file exists, ``False`` otherwise.
        """
        return os.path.isfile(self._make_absolute(filepath))

    def open(self, filepath, mode="rb", encoding=None):
        """Open a file in a specific mode.

        :param filepath: The local storage path of the file.
        :param mode: (optional) The file mode to open the file with.
        :param encoding: (optional) The encoding of the file to use in text mode.
        :return: The open file object.
        """
        # pylint: disable=consider-using-with
        return open(self._make_absolute(filepath), mode=mode, encoding=encoding)

    def close(self, file):
        """Close an open file.

        :param file: The file to close.
        """
        file.close()

    def _copy_file_content(self, dst, file, mode):
        dst_filesize = 0

        if mode == "a":
            try:
                dst_filesize = self.get_size(dst)
            except FileNotFoundError:
                pass

        try:
            # Assume the file exists on the file system at first, otherwise fall back to
            # checking the size of the binary stream.
            src_filesize = os.fstat(file.fileno()).st_size
        except:
            src_filesize = file.getbuffer().nbytes

        if self.max_size is not None and (dst_filesize + src_filesize > self.max_size):
            raise KadiFilesizeExceededError(
                f"File is larger than {filesize(self.max_size)}."
            )

        # pylint: disable=unspecified-encoding
        with open(self._make_absolute(dst), mode=f"{mode}b") as f:
            while True:
                buf = file.read(self.buffer_size)

                if not buf:
                    break

                f.write(buf)

    def save(self, dst, file_or_src, append=False):
        """Save a file or file-like object in a specific location.

        :param dst: The local destination storage path of the new file.
        :param file_or_src: A file-like object or binary stream to save or the name of
            an existing file to copy instead.
        :param append: (optional) Flag to indicate if an existing file should be
            overwritten (default) or appended to.
        :raises KadiFilesizeExceededError: If the maximum file size the storage was
            configured with would be exceeded when saving the file.
        """
        mode = "a" if append else "w"

        dst = self._make_absolute(dst)

        self.ensure_filepath_exists(dst)

        if isinstance(file_or_src, str):
            # file_or_src can be an external resource, so check if it is an absolute
            # path before passing it to _make_absolute, which would check if it is a
            # subdirectory of the root directory.
            file_or_src = (
                file_or_src
                if os.path.isabs(file_or_src)
                else self._make_absolute(file_or_src)
            )

            with open(file_or_src, mode="rb") as f:
                self._copy_file_content(dst, f, mode)
        else:
            self._copy_file_content(dst, file_or_src, mode)

    def move(self, src, dst):
        """Move a file to a specific location.

        Files can only be moved within this storage.

        :param src: The local source storage path of the file.
        :param dst: The local destination storage path of the file.
        """
        src = self._make_absolute(src)
        dst = self._make_absolute(dst)
        try:
            # Try renaming the file first, which only works if both files are on the
            # same file system.
            self.ensure_filepath_exists(dst)
            os.rename(src, dst)
        except OSError:
            self.save(dst, src)
            self.delete(src)

    def delete(self, filepath):
        """Delete a file if it exists.

        :param filepath: The local storage path of the file.
        """
        try:
            os.remove(self._make_absolute(filepath))
        except FileNotFoundError:
            pass

    def ensure_filepath_exists(self, filepath):
        """Ensures that the directory structure in the path exists.

        If the path is non existent, the complete structure is created.

        :param filepath: The local storage path of the file.
        """
        absolute_filepath = self._make_absolute(filepath)
        os.makedirs(os.path.dirname(absolute_filepath), exist_ok=True)

    def get_mimetype(self, filepath):
        """Get the MIME type of a file.

        Will determine the MIME type based on the given file's content.

        :param filepath: The local storage path of the file.
        :return: The MIME type of the file.
        """
        filepath = self._make_absolute(filepath)

        try:
            mimetype = magic.from_file(filepath, mime=True)
        except:
            return "application/octet-stream"

        # Both MIME types are interchangeable, but we prefer the returned one.
        if mimetype == "text/xml":
            return "application/xml"

        # Improve the detection of some common formats for reasonably small files that
        # libmagic may just detect as plain text.
        if mimetype == "text/plain" and self.get_size(filepath) < 10 * const.ONE_MB:
            try:
                with open(filepath, mode="rb") as f:
                    json.load(f)

                return "application/json"
            except:
                pass

            try:
                with open(filepath, mode="rb") as f:
                    parse(f)

                return "application/xml"
            except:
                pass

        return mimetype

    def get_size(self, filepath):
        """Get the size of a file.

        :param filepath: The local storage path of the file.
        :return: The size of the file in bytes.
        """
        return os.path.getsize(self._make_absolute(filepath))

    def validate_size(self, filepath, size, op="=="):
        """Validate the size of a file.

        :param filepath: The local storage path of the file.
        :param size: The size to compare the file with.
        :param op: (optional) The operator to use for comparison. See ``op`` in
            :func:`kadi.lib.utils.get_truth` for possible values.
        :raises KadiFilesizeMismatchError: If the validation failed.
        """
        filesize = self.get_size(filepath)

        if not get_truth(filesize, op, size):
            raise KadiFilesizeMismatchError(
                f"File size mismatch ({filesize} {op} {size})."
            )

    def get_checksum(self, filepath):
        """Get the MD5 checksum of a file.

        :param filepath: The local storage path of the file.
        :return: The MD5 checksum as string in hex representation.
        """
        filepath = self._make_absolute(filepath)
        checksum = hashlib.md5()

        with open(filepath, mode="rb") as f:
            while True:
                buf = f.read(self.buffer_size)

                if not buf:
                    break

                checksum.update(buf)

        return checksum.hexdigest()

    def validate_checksum(self, filepath, expected, actual=None):
        """Validate the checksum of a file.

        :param filepath: The local storage path of the file.
        :param expected: The excepted checksum as string in hex representation.
        :param actual: (Optional) The actual checksum calculated during the upload.
        :raises KadiChecksumMismatchError: If the checksums did not match.
        """
        checksum = actual or self.get_checksum(filepath)

        if checksum != expected:
            raise KadiChecksumMismatchError(
                f"File checksum mismatch (expected: {expected}, actual: {checksum})."
            )

    def create_filepath(self, file_identifier):
        """Create a path from a file identifier suitable for storing files.

        The structure of the path is dependent on the given storage type.

        :param file_identifier: The identifier of the file. This should generally be a
            file's internal, unique ID suitable for an actual file name, e.g. a UUID
            like in :attr:`.File.id`.
        :return: The created file path.
        """
        filepath = LocalStorage.filepath_from_name(
            file_identifier, dir_len=self.dir_len, num_dirs=self.num_dirs
        )

        return self._make_absolute(filepath)

    def _make_absolute(self, filepath):
        """Converts a path to an absolute path.

        Converts the path only to absolute if it is not already an absolute path.
        If it is already an absolute path it is ensured, that the path is a
        subdirectory of the root directory.

        :param filepath: The relative or absolute path.
        :return: The absolute path.
        :raises ValueError: The resulting path is not a subdirectory of the root
            directory.
        """
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.root_directory, filepath)

        filepath = os.path.realpath(filepath)

        # Check if the path is a subdirectory of the root directory.
        if not self._is_subdirectory_of_root(filepath):
            raise ValueError(
                f"Path '{filepath}' is not a subdirectory of the root directory "
                f"'{self.root_directory}'."
            )

        return filepath

    def _is_subdirectory_of_root(self, filepath):
        """Checks if the given filepath is the root directory or a subdirectory of it.

        :param filepath: The path to check.
        :return: ``True`` if the given path is part of the root directory.
        """
        return (
            os.path.commonpath([self.root_directory, os.path.realpath(filepath)])
            == self.root_directory
        )

    @property
    def root_directory(self):
        """Get the root directory."""
        return self._root_directory


def create_default_local_storage(root_directory=None, max_size=None):
    """Creates a default local storage.

    :param root_directory: (optional) Root directory of storage. If ``None`` the
        ``STORAGE_PATH`` from the config is used.
    :param max_size: (optional) See :class:`.BaseStorage`.
    :return: The storage.
    """

    if root_directory is None:
        root_directory = current_app.config["STORAGE_PATH"]

    return LocalStorage(root_directory=root_directory, max_size=max_size)
