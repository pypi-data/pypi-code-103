import contextlib
import errno
import os
import tarfile
import warnings
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import dials_data.datasets

if os.name == "posix":
    import fcntl

    def _platform_lock(file_handle):
        fcntl.lockf(file_handle, fcntl.LOCK_EX)

    def _platform_unlock(file_handle):
        fcntl.lockf(file_handle, fcntl.LOCK_UN)


elif os.name == "nt":
    import msvcrt

    def _platform_lock(file_handle):
        file_handle.seek(0)
        while True:
            try:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
                # Call will only block for 10 sec and then raise
                # OSError: [Errno 36] Resource deadlock avoided
                break  # lock obtained
            except OSError as e:
                if e.errno != errno.EDEADLK:
                    raise

    def _platform_unlock(file_handle):
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)


else:

    def _platform_lock(file_handle):
        raise NotImplementedError("File locking not supported on this platform")

    _platform_unlock = _platform_lock


@contextlib.contextmanager
def _file_lock(file_handle):
    """
    Cross-platform file locking. Open a file for writing or appending.
    Then a file lock can be obtained with:

    with open(filename, 'w') as fh:
      with _file_lock(fh):
        (..)
    """
    lock = False
    try:
        _platform_lock(file_handle)
        lock = True
        yield
    finally:
        if lock:
            _platform_unlock(file_handle)


@contextlib.contextmanager
def download_lock(target_dir):
    """
    Obtains a (cooperative) lock on a lockfile in a target directory, so only a
    single (cooperative) process can enter this context manager at any one time.
    If the lock is held this will block until the existing lock is released.
    """
    with target_dir.join(".lock").open(mode="w", ensure=True) as fh:
        with _file_lock(fh):
            yield


def _download_to_file(url, pyfile):
    """
    Downloads a single URL to a file.
    """
    with contextlib.closing(urlopen(url)) as socket:
        file_size = socket.info().get("Content-Length")
        if file_size:
            file_size = int(file_size)
        # There is no guarantee that the content-length header is set
        received = 0
        block_size = 8192
        # Allow for writing the file immediately so we can empty the buffer
        with pyfile.open(mode="wb", ensure=True) as f:
            while True:
                block = socket.read(block_size)
                received += len(block)
                f.write(block)
                if not block:
                    break

    if file_size and file_size != received:
        raise OSError(
            "Error downloading {url}: received {received} bytes instead of expected {file_size} bytes".format(
                file_size=file_size, received=received, url=url
            )
        )


def file_hash(path):
    """Returns the SHA256 digest of a file."""
    return path.computehash(hashtype="sha256")


def fetch_dataset(
    dataset,
    ignore_hashinfo=False,
    verify=False,
    read_only=False,
    verbose=False,
    pre_scan=True,
    download_lockdir=None,
):
    """Check for the presence or integrity of the local copy of the specified
    test dataset. If the dataset is not available or out of date then attempt
    to download/update it transparently.

    :param verbose:          Show everything as it happens.
    :param pre_scan:         If all files are present and all file sizes match
                             then skip file integrity check and exit quicker.
    :param read_only:        Only use existing data, never download anything.
                             Implies pre_scan=True.
    :returns:                False if the dataset can not be downloaded/updated
                             for any reason.
                             True if the dataset is present and passes a
                             cursory inspection.
                             A validation dictionary if the dataset is present
                             and was fully verified.
    """
    if dataset not in dials_data.datasets.definition:
        return False
    definition = dials_data.datasets.definition[dataset]

    target_dir = dials_data.datasets.repository_location().join(dataset)
    if read_only and not target_dir.check(dir=1):
        return False

    integrity_info = definition.get("hashinfo")
    if not integrity_info or ignore_hashinfo:
        integrity_info = dials_data.datasets.create_integrity_record(dataset)

    if "verify" not in integrity_info:
        integrity_info["verify"] = [{} for _ in definition["data"]]
    filelist = [
        {
            "url": source["url"],
            "file": target_dir.join(os.path.basename(urlparse(source["url"]).path)),
            "files": source.get("files"),
            "verify": hashinfo,
        }
        for source, hashinfo in zip(definition["data"], integrity_info["verify"])
    ]

    if pre_scan or read_only:
        if all(
            item["file"].check()
            and item["verify"].get("size")
            and item["verify"]["size"] == item["file"].size()
            for item in filelist
        ):
            return True
        if read_only:
            return False

    if download_lockdir:
        # Acquire lock if required as files may be downloaded/written.
        with download_lock(download_lockdir):
            _fetch_filelist(filelist, file_hash)
    else:
        _fetch_filelist(filelist, file_hash)

    return integrity_info


def _fetch_filelist(filelist, file_hash):
    for source in filelist:  # parallelize this
        if source.get("type", "file") == "file":
            valid = False
            if source["file"].check(file=1):
                # verify
                valid = True
                if source["verify"]:
                    if source["verify"]["size"] != source["file"].size():
                        valid = False
                        print("size")
                    elif source["verify"]["hash"] != file_hash(source["file"]):
                        valid = False
                        print(
                            "hash", source["verify"]["hash"], file_hash(source["file"])
                        )

            downloaded = False
            if not valid:
                print("Downloading {}".format(source["url"]))
                _download_to_file(source["url"], source["file"])
                downloaded = True

            # verify
            valid = True
            fileinfo = {
                "size": source["file"].size(),
                "hash": file_hash(source["file"]),
            }
            if source["verify"]:
                if source["verify"]["size"] != fileinfo["size"]:
                    valid = False
                elif source["verify"]["hash"] != fileinfo["hash"]:
                    valid = False
            else:
                source["verify"]["size"] = fileinfo["size"]
                source["verify"]["hash"] = fileinfo["hash"]

        # If the file is a tar archive, then decompress
        if source["files"]:
            target_dir = source["file"].dirpath()
            if downloaded or not all(
                (target_dir / f).check(file=1) for f in source["files"]
            ):
                # If the file has been (re)downloaded, or we don't have all the requested
                # files from the archive, then we need to decompress the archive
                print("Decompressing {file}".format(file=source["file"]))
                if source["file"].ext == ".zip":
                    with zipfile.ZipFile(source["file"].strpath) as zf:
                        try:
                            for f in source["files"]:
                                zf.extract(f, path=source["file"].dirname)
                        except KeyError:
                            print(
                                f"Expected file {f} not present in zip archive {source['file']}"
                            )
                else:
                    with tarfile.open(source["file"].strpath) as tar:
                        for f in source["files"]:
                            try:
                                tar.extract(f, path=source["file"].dirname)
                            except KeyError:
                                print(
                                    f"Expected file {f} not present in tar archive {source['file']}"
                                )


class DataFetcher:
    """A class that offers access to regression datasets.

    To initialize:
        df = DataFetcher()
    Then
        df('insulin')
    returns a py.path object to the insulin data. If that data is not already
    on disk it is downloaded automatically.

    To disable all downloads:
        df = DataFetcher(read_only=True)

    Do not use this class directly in tests! Use the dials_data fixture.
    """

    def __init__(self, read_only=False):
        self._cache = {}
        self._target_dir = dials_data.datasets.repository_location()
        self._read_only = read_only and os.access(self._target_dir.strpath, os.W_OK)

    def __repr__(self):
        return "<{}DataFetcher: {}>".format(
            "R/O " if self._read_only else "",
            self._target_dir.strpath,
        )

    def result_filter(self, result, **kwargs):
        """
        An overridable function to mangle lookup results.
        Used in tests to transform negative lookups to test skips.
        Overriding functions should add **kwargs to function signature
        to be forwards compatible.
        """
        return result

    def __call__(self, test_data, pathlib=None, **kwargs):
        """
        Return the location of a dataset, transparently downloading it if
        necessary and possible.
        The return value can be manipulated by overriding the result_filter
        function.
        :param test_data: name of the requested dataset.
        :param pathlib: Whether to return the result as a Python pathlib object.
                        The default for this setting is 'False' for now (leading
                        to a py.path.local object being returned), but the default
                        will change to 'True' in a future dials.data release.
                        Set to 'True' for forward compatibility.
        :return: A pathlib or py.path.local object pointing to the dataset, or False
                 if the dataset is not available.
        """
        if test_data not in self._cache:
            self._cache[test_data] = self._attempt_fetch(test_data, **kwargs)
        if pathlib is None:
            warnings.warn(
                "The DataFetcher currently returns py.path.local() objects. "
                "This will in the future change to pathlib.Path() objects. "
                "You can either add a pathlib=True argument to obtain a pathlib.Path() object, "
                "or pathlib=False to silence this warning for now.",
                DeprecationWarning,
                stacklevel=2,
            )
        if pathlib and self._cache[test_data]["result"]:
            result = {
                **self._cache[test_data],
                "result": Path(self._cache[test_data]["result"]),
            }
            return self.result_filter(**result)
        return self.result_filter(**self._cache[test_data])

    def _attempt_fetch(self, test_data):
        if self._read_only:
            data_available = fetch_dataset(test_data, pre_scan=True, read_only=True)
        else:
            data_available = fetch_dataset(
                test_data,
                pre_scan=True,
                read_only=False,
                download_lockdir=self._target_dir,
            )
        if data_available:
            return {"result": self._target_dir.join(test_data)}
        else:
            return {"result": False}
