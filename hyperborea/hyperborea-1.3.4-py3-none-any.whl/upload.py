import boto3
import collections
import ctypes
import datetime
import hashlib
import logging
import multiprocessing.connection
import os
import re
import sys
import time
import threading

from PySide2 import QtCore

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

logger = logging.getLogger(__name__)


def mark_file_for_upload(apd_filename):
    root, name = os.path.split(apd_filename)
    upload_filename = os.path.join(root, "." + name + ".upload")
    if not os.path.exists(upload_filename):
        upload_file = open(upload_filename, 'w', encoding="ascii")
        upload_file.close()
        if sys.platform == "win32":
            # make the file hidden on windows
            # the leading . in the filename is enough for linux
            ctypes.windll.kernel32.SetFileAttributesW(upload_filename, 0x02)


class LockFile:
    def __init__(self, lockfilename):
        self.lockfilename = lockfilename
        self.lockfile = None

    def __enter__(self):
        self.lockfile = open(self.lockfilename, 'r+', encoding="ascii")
        if sys.platform == "win32":
            msvcrt.locking(self.lockfile.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.lockf(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        if sys.platform == "win32":
            msvcrt.locking(self.lockfile.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.lockf(self.lockfile, fcntl.LOCK_UN)
        self.lockfile.close()
        self.lockfile = None


class UploadManager(QtCore.QObject):
    upload_status = QtCore.Signal(str, object, object)  # name, sent, total
    rate_status = QtCore.Signal(bool, float)
    error = QtCore.Signal()
    started = QtCore.Signal()

    def __init__(self, base_dir, s3_bucket, key_prefix, access_key_id,
                 secret_access_key, aws_region, delete_after_upload,
                 rate_update_interval=None, rate_average_period=None):
        super().__init__()

        self.base_dir = base_dir
        self.s3_bucket = s3_bucket
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.delete_after_upload = delete_after_upload
        self.rate_update_interval = rate_update_interval
        self.rate_average_period = rate_average_period
        if rate_update_interval is None or rate_average_period is None:
            self.rate_enabled = False
        else:
            self.rate_enabled = True

        # make sure there are no leading or trailing slashes (or backslashes)
        self.key_prefix = key_prefix.strip("\\/")

        # create the S3 client
        self.s3_client = boto3.client('s3', aws_access_key_id=access_key_id,
                                      aws_secret_access_key=secret_access_key,
                                      region_name=aws_region)

        self.scan_interval = 5 * 60
        self.scan_ignore_newer = 20 * 60

        self.is_finished = threading.Event()
        self.upload_order = collections.deque()
        self.upload_thread = threading.Thread(target=self._upload_loop)

        self._scan_dir()
        self.scan_thread = threading.Thread(target=self._scan_loop)

        # rate calculations
        self.uploading = False
        self.rate_lock = threading.Lock()
        self.rate_byte_count = 0  # total of items in rate_deque
        self.rate_deque = collections.deque()
        if self.rate_enabled:
            self.rate_thread = threading.Thread(target=self._rate_loop)
        else:
            self.rate_thread = None

        # upload pipes from other processes
        self.pipe_lock = threading.Lock()
        self.pipe_list = []
        self.pipe_thread = threading.Thread(target=self._pipe_loop)

        # start
        self.upload_thread.start()
        self.scan_thread.start()
        self.pipe_thread.start()
        if self.rate_thread is not None:
            self.rate_thread.start()

    def _scan_dir(self):
        now = time.time()

        # search the directory for .upload files
        found = []
        for root, _dirs, files in os.walk(self.base_dir):
            for name in files:
                if name.endswith(".upload"):
                    uploadfilename = os.path.join(root, name)
                    if name.startswith("."):
                        # remove "." at front
                        name = name[1:]
                    filename = os.path.join(root, name[:-len(".upload")])
                    if filename not in self.upload_order:
                        try:
                            mtime = os.path.getmtime(filename)
                            # see if the .upload file is empty (i.e. finished)
                            if os.path.getsize(uploadfilename) == 0:
                                found.append((mtime, filename))
                            else:
                                # never finished writing. either crashed or
                                # still going on. See if it's older than 20 min
                                if mtime + self.scan_ignore_newer < now:
                                    found.append((mtime, filename))
                                elif now + self.scan_ignore_newer < mtime:
                                    logger.warning("File mtime in future: %s",
                                                   filename)
                                else:
                                    logger.debug("File not ready: %s",
                                                 filename)
                        except FileNotFoundError:
                            continue
        # add found files to the upload queue, newer entries popped first
        for _mtime, filename in sorted(found):
            logger.info("Directory scan found %s", filename)
            self.upload_order.append(filename)

    def _scan_loop(self):
        try:
            while True:
                if self.is_finished.wait(self.scan_interval):
                    # finished, break out of loop
                    break
                else:
                    # time for scan
                    self._scan_dir()
        except Exception:
            logger.exception("Uncaught exception in scan_loop")
            self.stop()
            self.error.emit()

    def _upload_loop(self):
        try:
            emitted_error = False

            while True:
                if self.is_finished.is_set():
                    return

                try:
                    # check if the bucket exists to verify things work
                    self.s3_client.head_bucket(Bucket=self.s3_bucket)
                    break
                except Exception:
                    if not emitted_error:
                        emitted_error = True
                        logger.exception("Error connecting to S3 bucket")
                        self.error.emit()
                    # put a delay in so it's not contantly hitting the server
                    if self.is_finished.wait(20.0):
                        return
                    continue

            logger.debug("Uploader started")
            self.started.emit()

            while True:
                # see if anything is ready for upload
                try:
                    filename = self.upload_order[-1]
                    self._do_upload(filename)
                    self.upload_order.remove(filename)
                except IndexError:
                    self.uploading = False

                    # short delay when empty; no need to max out CPU
                    time.sleep(0.1)

                if self.is_finished.is_set():
                    return
        except Exception:
            logger.exception("Uncaught exception in upload_loop")
            self.stop()
            self.error.emit()

    def _get_rate(self):
        # prune any old entries
        now = datetime.datetime.utcnow()
        bytes_too_old = 0
        cutoff_time = now - datetime.timedelta(
            seconds=self.rate_average_period)
        while len(self.rate_deque):
            sent_dt, sent_bytes = self.rate_deque[0]
            if sent_dt < cutoff_time:
                bytes_too_old += sent_bytes
                self.rate_deque.popleft()
            else:
                break
        with self.rate_lock:
            # update the byte count inside the lock
            self.rate_byte_count -= bytes_too_old

            local_count = self.rate_byte_count
            deque_entries = len(self.rate_deque)

            if deque_entries == 0:
                return 0.0
            elif deque_entries == 1:
                # taper off as the entry moves toward exprining
                only_dt, byte_total = self.rate_deque[0]
                duration = (only_dt - cutoff_time).total_seconds()
                if duration > 0:
                    taper = (duration / self.rate_average_period)
                    return (byte_total / self.rate_average_period) * taper
                else:
                    return 0.0
            else:
                # use oldest entry for duration, but not byte_total
                last_dt, last_bytes = self.rate_deque[0]
                first_dt, _first_bytes = self.rate_deque[-1]
                byte_total = local_count - last_bytes
                duration = (first_dt - last_dt).total_seconds()
                if duration > 0:
                    return byte_total / duration
                else:
                    return 0.0

    def _rate_loop(self):
        try:
            while True:
                if self.is_finished.wait(self.rate_update_interval):
                    # finished, break out of loop
                    break
                else:
                    # time for signal
                    self.rate_status.emit(self.uploading, self._get_rate())
        except Exception:
            logger.exception("Uncaught exception in rate_loop")
            self.stop()
            self.error.emit()

    def _get_file_md5(self, file):
        md5 = hashlib.md5()
        for chunk in iter(lambda: file.read(4096), b""):
            md5.update(chunk)
        file.seek(0, 0)  # go back to the beginning
        return md5.hexdigest()

    def _do_upload_s3(self, file, filelen):
        # figure out the S3 key name
        relpath = os.path.relpath(file.name, start=self.base_dir)
        relpath = os.path.join(self.key_prefix, relpath)
        keyname = relpath.replace("\\", "/")  # S3 uses only forward slashes

        basename = os.path.basename(file.name)

        # get the key prefix
        next_index = 1
        prefix, prefix_ext = os.path.splitext(keyname)
        if prefix.endswith(")"):
            m = re.match("^(.*)\(([0-9]*?)\)$", prefix)
            if m:
                prefix = m.group(1)
                next_index = int(m.group(2)) + 1

        obj_list = self.s3_client.list_objects_v2(Bucket=self.s3_bucket,
                                                  Prefix=prefix)
        if 'Contents' in obj_list:
            existing_keys = set()
            md5_digest = self._get_file_md5(file)
            for key_info in obj_list['Contents']:
                k = key_info.get("Key", "")
                if not k:
                    logger.warning("Missing key on prefix %s", prefix)
                existing_keys.add(k)

                etag = key_info.get('ETag', '').strip('"\'')
                if not etag:
                    logger.warning("Missing tag for %s", k)
                elif etag == md5_digest:
                    logger.info("Skipping duplicate upload %s", basename)
                    return

            while keyname in existing_keys:
                # need to rename x.apd to x(1).apd, or x(1).apd to x(2).apd
                keyname = prefix + "(" + str(next_index) + ")" + prefix_ext
                next_index += 1

        total_sent_bytes = 0

        def callback(sent_bytes):
            nonlocal total_sent_bytes

            if self.rate_enabled:
                now = datetime.datetime.utcnow()
                with self.rate_lock:
                    self.rate_byte_count += sent_bytes
                self.rate_deque.append((now, sent_bytes))

            total_sent_bytes += sent_bytes

            self.upload_status.emit(basename, total_sent_bytes, filelen)

        extra_args = {'StorageClass': 'STANDARD_IA'}
        self.uploading = True
        start_time = time.monotonic()
        self.s3_client.upload_fileobj(file, self.s3_bucket, keyname,
                                      Callback=callback, ExtraArgs=extra_args)
        end_time = time.monotonic()

        duration = end_time - start_time
        if duration > 0:
            avg_rate = filelen / duration
        else:
            avg_rate = 0.0

        logger.info("Finished upload %s (%.0fkB, %.0fs, %.1fkB/s)",
                    basename, filelen / 1000, duration, avg_rate / 1000)

    def _do_upload(self, filename):
        try:
            path, name = os.path.split(filename)
            lockfilename = os.path.join(path, "." + name + ".upload")
            with LockFile(lockfilename):
                with open(filename, 'rb') as file:
                    file.seek(0, os.SEEK_END)
                    filelen = file.tell()
                    file.seek(0, os.SEEK_SET)

                    # do the actual upload
                    try:
                        self._do_upload_s3(file, filelen)
                    except Exception:
                        logger.exception("Error uploading: %s", filename)
                        return
        except OSError:
            logger.warning("Can't upload, file in use: %s", filename)
            return

        try:
            # finished uploading, so delete the .upload marker file
            os.remove(lockfilename)
        except Exception:
            logger.exception("Error removing upload file: %s", lockfilename)
            return

        if self.delete_after_upload:
            try:
                os.remove(filename)

                # try removing empty directories recursively up to base_dir
                try:
                    relpath = os.path.relpath(filename, self.base_dir)
                    relative_dir = os.path.dirname(relpath)
                    while relative_dir:
                        os.rmdir(os.path.join(self.base_dir, relative_dir))
                        relative_dir = os.path.dirname(relative_dir)
                except OSError:
                    pass  # directory not empty, no problem
            except Exception:
                logger.exception("Error removing file: %s", filename)

    def upload(self, filename):
        if filename not in self.upload_order:
            logger.debug("File ready for upload: %s", filename)
            self.upload_order.append(filename)

    def _pipe_loop(self):
        try:
            while True:
                if self.is_finished.is_set():
                    return

                with self.pipe_lock:
                    pipe_list_copy = self.pipe_list.copy()

                if not pipe_list_copy:
                    self.is_finished.wait(0.1)
                    continue

                ready = multiprocessing.connection.wait(pipe_list_copy,
                                                        timeout=0.1)
                for pipe in ready:
                    try:
                        ready_file = pipe.recv()
                        if ready_file is None:
                            # None signals that this pipe is done
                            with self.pipe_lock:
                                self.pipe_list.remove(pipe)
                        else:
                            self.upload(ready_file)
                    except EOFError:
                        with self.pipe_lock:
                            self.pipe_list.remove(pipe)
        except Exception:
            logger.exception("Uncaught exception in pipe_loop")
            self.stop()
            self.error.emit()

    def register_upload_pipe(self, pipe):
        with self.pipe_lock:
            self.pipe_list.append(pipe)

    def stop(self):
        self.is_finished.set()

    def join(self):
        self.upload_thread.join()
        self.scan_thread.join()
        if self.rate_thread is not None:
            self.rate_thread.join()

    def rescan(self):
        self._scan_dir()
