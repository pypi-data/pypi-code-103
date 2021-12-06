import functools
import logging
import threading
import urllib.parse

from PySide2 import QtCore
import requests

logger = logging.getLogger(__name__)


class _Fetcher(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

    def start(self, url, log_type, timeout=None):
        self.request_thread = threading.Thread(
            target=self.request_thread_run, args=(url, log_type, timeout))
        self.request_thread.start()

    def request_thread_run(self, url, log_type, timeout):
        try:
            logger.info("Requesting %s from url %s", log_type, url)
            response = requests.get(url)

            if not response.ok:
                logger.error("Error requesting %s: %s", log_type,
                             response.text)
                self.error.emit(f"Error requesting {log_type}!")
                return

            data = response.json()

            if not data:
                logger.error("Empty response for %s request!", log_type)
                self.error.emit(f"Error requesting {log_type}!")
                return

            self.completed.emit(data)
        except Exception:
            logger.exception('Error requesting %s', log_type)
            self.error.emit(f"Error requesting {log_type}!")


class FirmwareFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

    def find_firmware(self, build_type, board_info=None, repo=None,
                      branch=None, commit=None, timeout=None):
        keys = []
        # need either board_info or repo, but not both
        if board_info:
            if repo:
                raise ValueError("Cannot specify both board_info and repo")
            else:
                board_name, board_rev = board_info
                keys.append("boardname={}".format(
                    urllib.parse.quote(board_name)))
                keys.append("boardrev={}".format(board_rev))
        else:
            if repo:
                keys.append("repo={}".format(urllib.parse.quote(repo)))
            else:
                raise ValueError("Must specify one of board_info or repo")

        # need at most one of branch and commit
        if commit and branch:
            raise ValueError("Cannot specify both commit and branch")
        elif commit is not None:
            keys.append("hash={}".format(commit))
        elif branch is not None:
            keys.append("branch={}".format(branch))

        base_url = "https://api.suprocktech.com/firmwareinfo/findfirmware"
        url = base_url + "?" + "&".join(keys)

        self.fetcher = _Fetcher()
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(
            functools.partial(self.got_data, build_type=build_type))
        self.fetcher.start(url, "findfirmware", timeout)

    def got_data(self, build_urls, build_type):
        try:
            if build_type is not None and build_type in build_urls:
                build_urls = {build_type: build_urls[build_type]}
            self.completed.emit(build_urls)
        except Exception:
            logger.exception('Error finding firmware')
            self.error.emit('Unknown error finding firmware!')


class SoftwareFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

    def find_software(self, repo, build_key, branch=None, commit=None,
                      timeout=None):
        base_url = "https://api.suprocktech.com/software/findsoftware"
        keys = ["repo={}".format(repo), "key={}".format(build_key)]
        if commit:
            keys.append("hash={}".format(commit))
        if branch:
            keys.append("branch={}".format(branch))

        url = base_url + "?" + "&".join(keys)

        self.fetcher = _Fetcher()
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(self.got_data)
        self.fetcher.start(url, "findsoftware", timeout)

    def got_data(self, values):
        try:
            if "url" not in values:
                logger.error("Empty response to findsoftware!")
                self.error.emit("Error requesting software information!")
                return

            url = values['url']
            commit = values.get('commit', None)
            state = values.get('state', "SUCCESSFUL")
            ready = (state == "SUCCESSFUL")

            self.completed.emit((url, commit, ready))
        except Exception:
            logger.exception('Error finding software')
            self.error.emit("Unknown error finding software!")


class RefFinder(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        self.fetcher = _Fetcher()
        self.fetcher.error.connect(self.error)
        self.fetcher.completed.connect(self.completed)

    def get_software_refs(self, repo, timeout=None):
        base_url = "https://api.suprocktech.com/software/findsoftware"
        keys = ["repo={}".format(repo), "listrefs=1"]

        url = base_url + "?" + "&".join(keys)

        self.fetcher.start(url, "listrefs", timeout)

    def get_firmware_refs(self, board_info=None, repo=None, timeout=None):
        keys = ["listrefs=1"]
        # need either board_info or repo, but not both
        if board_info:
            if repo:
                raise ValueError("Cannot specify both board_info and repo")
            else:
                board_name, board_rev = board_info
                keys.append("boardname={}".format(
                    urllib.parse.quote(board_name)))
                keys.append("boardrev={}".format(board_rev))
        else:
            if repo:
                keys.append("repo={}".format(urllib.parse.quote(repo)))
            else:
                raise ValueError("Must specify one of board_info or repo")

        base_url = "https://api.suprocktech.com/firmwareinfo/findfirmware"
        url = base_url + "?" + "&".join(keys)

        self.fetcher.start(url, "listrefs", timeout)


class Downloader(QtCore.QObject):
    completed = QtCore.Signal(object)
    error = QtCore.Signal(object, str)

    def __init__(self):
        super().__init__()

    def start_download(self, url, file, update):
        self.download_thread = threading.Thread(
            target=self.download_thread_run, args=(url, file, update))
        self.download_thread.start()

    def download_thread_run(self, url, file, update):
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_length = r.headers.get('content-length')
                written_bytes = 0
                if total_length:
                    total_length = int(total_length)
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        file.write(chunk)
                        written_bytes += len(chunk)
                        if update and total_length:
                            update(written_bytes, total_length)
                self.completed.emit(file)
        except Exception:
            logger.exception('Error downloading file')
            self.error.emit(file, 'Error downloading file')
