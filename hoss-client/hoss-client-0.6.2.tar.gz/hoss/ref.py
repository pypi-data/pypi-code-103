from typing import Optional, TYPE_CHECKING, Dict

import io
import re
import fnmatch
import contextlib
import datetime

from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from hoss.namespace import Namespace


class DatasetRef:
    def __init__(self, namespace: 'Namespace', parent: Optional['DatasetRef'], dataset_name: str,
                 key: str, name: str,
                 etag: Optional[str], last_modified: Optional[datetime.datetime], size_bytes: Optional[int]):
        """

        Args:
            namespace: the Namespace object that contains this dataset
            parent: the parent ref. For the Dataset itself, this will be None.
            dataset_name: the name of the dataset that contains this ref
            key: the key to the ref
            name: the name of the ref (i.e. the name of the object without the "path")
            etag: the etag of the object
            last_modified: the last modified datetime of the object in the store
            size_bytes: the size of the object in bytes
        """
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.parent = parent
        self.key = key
        self.name = name
        self.uri = f"hoss+{namespace.base_url}:{dataset_name}:{key}"

        self._etag = etag
        self._last_modified = last_modified
        self._size_bytes = size_bytes

        self._metadata = None

        if '/' in name[:-1]:
            base_key = key[:len(key)-len(name)]

            parts = name.split('/')
            part = parts.pop()
            if part == '':  # it's a directory
                self.name = parts.pop() + '/'
            else:
                self.name = part

            for part in parts:
                base_key = f"{base_key}{part}/"
                self.parent = DatasetRef(self.namespace, self.parent, self.dataset_name, base_key, part + '/',
                                         etag=None, last_modified=None, size_bytes=None)

    def _populate_head_data(self) -> None:
        """Helper method to update the instance with data from a HEAD request"""
        try:
            data = self.namespace.object_store.head_object(self.namespace.name, self.namespace.bucket, self.key)
        except ClientError as err:
            if err.response['Error']['Code'] == '404':
                # If the object isn't found...it doesn't exist! Just return since no metadata exists.
                return
            else:
                raise

        self._metadata = data['metadata']

        # Metadata is case-insensitive, so we always enforce this for the user.
        if self._metadata:
            self._metadata = dict((k.lower(), str(v).lower()) for k, v in self._metadata.items())
        self._etag = data['etag']
        self._size_bytes = data['size_bytes']
        self._last_modified = data['last_modified']

    @property
    def metadata(self) -> dict:
        """Getter for the ref's metadata key-value pairs"""
        if not self._metadata:
            self._populate_head_data()
        return self._metadata

    @property
    def etag(self) -> str:
        """Getter for the etag of the object. The etag is a hash and will change when the file's contents change"""
        if not self._etag:
            self._populate_head_data()
        return self._etag

    @property
    def last_modified(self) -> datetime.datetime:
        """Getter for the last modified datetime in the object store backend"""
        if not self._last_modified:
            self._populate_head_data()

        return self._last_modified

    @property
    def size_bytes(self) -> int:
        """Getter for the size of the objects in bytes"""
        if not self._last_modified:
            self._populate_head_data()

        return self._size_bytes

    def __repr__(self):
        return f"<DatasetRef: {self.key}>"

    def __truediv__(self, name) -> 'DatasetRef':
        """Method to implement the `/` operator like how pathlib lets you build paths"""
        if name[0] == '/':
            name = name[1:]

        if self.is_dir():
            key = self.key + name
        else:
            key = self.key + '/' + name

        return DatasetRef(self.namespace, self, self.dataset_name, key, name,
                          etag=None, last_modified=None, size_bytes=None)

    def copy_to(self, target) -> None:
        """Method to copy the contents of 1 reference to another

        Args:
            target: A target ref to copy to

        Returns:
            None
        """
        if type(target) != DatasetRef:
            raise ValueError("target should be a DatasetRef")

        self.namespace.object_store.copy_object(self.namespace.name, self.namespace.bucket, self.key, target.key)

    def exists(self):
        return self.namespace.object_store.object_exists(self.namespace.name, self.namespace.bucket, self.key)

    def glob(self, pattern):
        if pattern.startswith("**/"):
            # cannot just return the rglob generator as this method is also a generator
            for ref in self.rglob(pattern):
                yield ref
            return

        compiled = re.compile(fnmatch.translate(pattern))
        for ref in self.namespace.object_store.list_objects(self.namespace.name, self.namespace.bucket, self.key):
            if compiled.match(ref["name"]) is not None:
                yield DatasetRef(self.namespace, self, self.dataset_name, ref['key'], ref['name'],
                                 ref['etag'], ref['last_modified'], ref['size_bytes'])

    def is_file(self):
        return not self.is_dir()

    def is_dir(self):
        return self.key[-1] == '/'

    def iterdir(self):
        return [DatasetRef(self.namespace, self, self.dataset_name, ref['key'], ref['name'],
                           ref['etag'], ref['last_modified'], ref['size_bytes'])
                for ref in self.namespace.object_store.list_objects(self.namespace.name,
                                                                    self.namespace.bucket,
                                                                    self.key)]

    def move(self, target):
        if type(target) != DatasetRef:
            raise ValueError("target should be a DatasetRef")

        self.copy_to(target)
        try:
            self.remove()
        except Exception as err:
            err_msg = f"Failed to remove source object during move operation: {err}"
            try:
                target.remove()
            except Exception as err:
                err_msg = f"{err_msg}. Failed to remove target object while rolling back move operation: {err}"
            finally:
                raise Exception(err_msg)

    @contextlib.contextmanager
    def open(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        buf = io.BytesIO()

        if 'r' in mode or 'a' in mode:
            self.read_to(buf)

        if 'r' in mode:
            buf.seek(0, 0)  # seek beginning

        if 'a' in mode:
            buf.seek(0, 2)  # seek end

        if 'b' not in mode:
            wrap = io.TextIOWrapper(buf,
                                    encoding=encoding,
                                    errors=errors,
                                    newline=newline,
                                    line_buffering=(buffering == 1),
                                    write_through=(buffering == 0))

        try:
            if 'b' not in mode:
                yield wrap
            else:
                yield buf
        finally:
            if 'b' not in mode:
                wrap.flush()

            if 'r' not in mode and '+' not in mode:
                buf.seek(0, 0) # rewind so all data is uploaded
                self.write_from(buf)

            if not buf.closed:
                buf.close()

    def read_bytes(self):
        return self.namespace.object_store.get_object(self.namespace.name, self.namespace.bucket, self.key)

    def read_text(self, encoding='utf-8'):
        return str(self.read_bytes(), encoding=encoding)

    def read_to(self, fh_or_name):
        if type(fh_or_name) == str:
            return self.namespace.object_store.download_file(self.namespace.name, self.namespace.bucket,
                                                             self.key, fh_or_name)
        else:
            if hasattr(fh_or_name, "mode") and 'b' not in fh_or_name.mode:
                raise ValueError("Can only read_to as binary data")
            if type(fh_or_name) == io.StringIO:
                raise ValueError("Can only read_to as binary data")
            return self.namespace.object_store.download_fileobj(self.namespace.name, self.namespace.bucket,
                                                                self.key, fh_or_name)

    def remove(self):
        self.unlink(missing_ok=True)

    def rglob(self, pattern):  # recursive glob - same as glob with `**/` at the start
        if pattern.startswith("**/"):
            pattern = pattern[1:]

        compiled = re.compile(fnmatch.translate(pattern))
        for ref in self.namespace.object_store.list_objects(self.namespace.name,
                                                            self.namespace.bucket,
                                                            self.key, recursive=True):
            key_part = ref['key'][len(self.key)-1:]  # leave the initial '/'
            if compiled.match(key_part) is not None:
                yield DatasetRef(self.namespace, self, self.dataset_name, ref['key'], ref['name'],
                                 ref['etag'], ref['last_modified'], ref['size_bytes'])

    def touch(self, exists_ok=True):
        if self.exists():
            if not exists_ok:
                raise FileExistsError(f"File {self.uri} already exists")
        else:
            self.write_bytes(b'')

    def unlink(self, missing_ok=False):
        if self.exists():
            self.namespace.object_store.delete_object(self.namespace.name, self.namespace.bucket, self.key)
        else:
            if not missing_ok:
                raise FileNotFoundError(f"File {self.uri} doesn't exist")

    def write_bytes(self, data, metadata: Optional[dict] = None):
        """Method to write bytes to a ref

        Args:
            data: binary data to write to the ref
            metadata: dictionary of metadata tags of type Dict[str, str]. If None and the reference already has
                      metadata tags, they will be persisted. If set to an empty dict() all keys will be removed.

        Returns:
            None
        """
        if metadata is None and self.metadata is not None:
            # If the user hasn't provided metadata, but this reference already has some, don't lose it
            metadata = self.metadata
        elif metadata is not None:
            # If metadata is set, update the local reference to save a HEAD operation
            # Also lower case keys and values since metadata is case insensitive.
            metadata = dict((k.lower(), str(v).lower()) for k, v in metadata.items())
            self._metadata = metadata

        # Reset properties we'd want to re-fetch if the user requests them after the write
        self._etag = None
        self._last_modified = None
        self._size_bytes = None

        self.namespace.object_store.put_object(self.namespace.name, self.namespace.bucket, self.key, data,
                                               metadata=metadata)

    def write_text(self, data: str, encoding: str = 'utf-8', metadata: Optional[Dict[str, str]] = None) -> None:
        """Method to write text to a ref

        Args:
            data: string to write to the ref
            encoding: encoding to use when converting from text to binary
            metadata: dictionary of metadata tags of type Dict[str, str]. If None and the reference already has
                      metadata tags, they will be persisted. If set to an empty dict() all keys will be removed.

        Returns:
            None
        """
        self.write_bytes(data.encode(encoding=encoding), metadata=metadata)

    def write_from(self, fh_or_name, metadata: Optional[dict] = None):
        """Method to write from a file handle OR a string containing an absolute file path

        Args:
            fh_or_name: file handle or absolute path to a file
            metadata: dictionary of metadata tags of type Dict[str, str]. If None and the reference already has
                      metadata tags, they will be persisted. If set to an empty dict() all keys will be removed.

        Returns:
            None
        """
        if metadata is None and self.metadata is not None:
            # If the user hasn't provided metadata, but this reference already has some, don't lose it
            metadata = self.metadata
        elif metadata is not None:
            # If metadata is set, update the local reference to save a HEAD operation
            # Also lower case keys and values since metadata is case insensitive.
            metadata = dict((k.lower(), str(v).lower()) for k, v in metadata.items())
            self._metadata = metadata

        # Reset properties we'd want to re-fetch if the user requests them after the write
        self._etag = None
        self._last_modified = None
        self._size_bytes = None

        if type(fh_or_name) == str:
            return self.namespace.object_store.upload_file(self.namespace.name, self.namespace.bucket,
                                                           self.key, fh_or_name, metadata=metadata)
        else:
            if hasattr(fh_or_name, "mode") and 'b' not in fh_or_name.mode:
                raise ValueError("Can only write_from as binary data")
            if type(fh_or_name) == io.StringIO:
                raise ValueError("Can only write_from as binary data")
            return self.namespace.object_store.upload_fileobj(self.namespace.name, self.namespace.bucket,
                                                              self.key, fh_or_name,  metadata=metadata)
