import binascii
import ctypes
import datetime
import json
import logging
import lzma
import os.path
import queue
import re
import struct
import subprocess
import sys
import threading
import time
import unicodedata

import asphodel
import hyperborea.proxy

logger = logging.getLogger(__name__)


instances = {}


def start_streaming(device, *args, **kwargs):
    device_logger = hyperborea.proxy.get_device_logger(logger, device)
    device_logger.debug("Starting streaming instance")

    if device in instances:
        stop_streaming(device)

    instance = StreamManager(device, device_logger, *args, **kwargs)
    instances[device] = instance
    instance.start()

    hyperborea.proxy.register_device_cleanup(device, stop_streaming)
    hyperborea.proxy.register_device_cleanup(None, join_streaming, instance,
                                             device_logger)


def stop_streaming(device):
    if device not in instances:
        return

    instances[device].stop()

    device_logger = hyperborea.proxy.get_device_logger(logger, device)
    device_logger.debug("Stopped streaming instance")

    del instances[device]

    hyperborea.proxy.unregister_device_cleanup(device, stop_streaming)


def join_streaming(_device, instance, device_logger):
    # called during cleanup, on proxy exit

    instance.join()
    device_logger.debug("Finished streaming instance")

    hyperborea.proxy.unregister_device_cleanup(None, join_streaming,
                                               instance, device_logger)


def get_valid_filename(s):
    # remove any non-ascii characters, and convert accents to closest ascii
    b = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    s = b.decode("ascii")

    # make any spaces into underscores
    s = s.strip().replace(" ", "_")

    # remove anything that's not alphanumeric, dash, underscore, dot
    s = re.sub(r'[^-\w.]', "", s)

    # reduce any strings of dots to a single dot
    s = re.sub(r'[.]{2,}', ".", s)

    # remove any leading or trailing dots
    s = s.strip(".")

    return s


class StreamWriter:
    def __init__(self, logger, header_dict, device_name, base_dir,
                 compression_level, upload_pipe):
        self.logger = logger
        self.header_dict = header_dict

        self.device_name = get_valid_filename(device_name)
        self.base_dir = base_dir

        self.compression_level = compression_level
        if self.compression_level is None:
            self.compression_level = lzma.PRESET_DEFAULT

        self.upload_pipe = upload_pipe

        self.next_boundary = None
        self.current_filename = None
        self.compressor_pipe = None
        self.compressor_lock = threading.Lock()
        self.compressors = {}
        self.finished_queue = queue.Queue()
        self.monitor_thread = threading.Thread(target=self.monitor_loop)

        self.packet_leader_struct = struct.Struct(">dI")

        self.is_finished = threading.Event()
        self.write_loop_exited = threading.Event()
        self.write_queue = queue.Queue()
        self.write_thread = threading.Thread(target=self.write_loop)

        self.create_header()
        self.create_compressor_args()
        self.write_thread.start()
        self.monitor_thread.start()

    def create_header(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()

        def type_convert(t):
            if t is None:
                return t
            elif isinstance(t, (int, bool, str, float)):
                return t
            elif isinstance(t, bytes):
                return binascii.b2a_hex(t).decode('ascii')
            elif isinstance(t, (list, tuple)):
                return [type_convert(x) for x in t]
            elif isinstance(t, dict):
                return {k: type_convert(v) for k, v in t.items()}
            else:
                try:
                    return t.to_json_obj()
                except AttributeError:
                    return repr(t)

        d = type_convert(self.header_dict)
        hb = json.dumps(d, ensure_ascii=True).encode('ascii')

        self.header_bytes = (struct.pack(">dI", timestamp, len(hb)) + hb)

    def _find(self, prog, paths):
        for path in paths:
            exe_file = os.path.join(path, prog)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                return exe_file
        return None

    def _find_7zip(self):
        # see if the included 7zip is available (win32 only)
        if sys.platform == "win32":
            is_64bit = sys.maxsize > (2 ** 32)
            if is_64bit:
                d = os.path.join(os.path.dirname(__file__), "7zip_64bit")
            else:
                d = os.path.join(os.path.dirname(__file__), "7zip_32bit")
            result = self._find('7za.exe', [d])
            if result:
                return result

        paths = os.environ["PATH"].split(os.pathsep)

        if sys.platform == "win32":
            program_files_keys = ['PROGRAMW6432', 'PROGRAMFILES',
                                  'PROGRAMFILES(X86)']
            program_files_dirs = []
            for key in program_files_keys:
                try:
                    path = os.environ[key]
                    if path:
                        program_files_dirs.append(path)
                except KeyError:
                    pass

            for program_files in program_files_dirs:
                paths.append(os.path.join(program_files, "7-Zip"))

            progs = ['7zr.exe', '7za.exe', '7z.exe']
        else:
            progs = ['7zr', '7za', '7z']

        for prog in progs:
            result = self._find(prog, paths)
            if result:
                return result
        return None

    def _find_xz(self):
        paths = os.environ["PATH"].split(os.pathsep)
        if sys.platform == "win32":
            return self._find("xz.exe", paths)
        else:
            return self._find("xz", paths)

    def create_compressor_args(self):
        if sys.platform == "win32":
            # create a new process group so that ctrl+c doesn't get forwarded
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self.popen_extras = {
                'startupinfo': startupinfo,
                'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            # hyperborea.proxy has this process in a different process group
            self.popen_extras = {}

        # find 7zip (7za, 7zr, 7z)
        compressor_path = self._find_7zip()
        if compressor_path:
            self.compressor_args = [
                compressor_path, 'a', '-si', '-txz', '-m0=lzma2',
                '-mx={}'.format(self.compression_level)]

            # 7zip writes the file directly (and needs file at the end of args)
            self.compressor_uses_stdout = False

            cmd_str = " ".join(self.compressor_args)
            self.logger.debug("Using 7zip compressor: {}".format(cmd_str))
            return

        # find xz
        compressor_path = self._find_xz()
        if compressor_path:
            self.compressor_args = [
                compressor_path, '-z', '-{}'.format(self.compression_level)]

            # xz writes to stdout
            self.compressor_uses_stdout = True

            cmd_str = " ".join(self.compressor_args)
            self.logger.debug("Using XZ compressor: {}".format(cmd_str))
            return

        # fall back to internal lzma module
        self.compressor_args = None
        self.logger.debug("Using internal lzma compressor")

    def open_compressor(self, dt):
        # figure out where to store the files, and make the dir (if needed)
        directory = os.path.join(self.base_dir, dt.strftime("%Y_%m_%d"),
                                 self.device_name)
        os.makedirs(directory, exist_ok=True)

        basename = os.path.join(directory, dt.strftime("%Y%m%dT%H%MZ_") +
                                self.device_name)

        filename = basename + ".apd"
        index = 1
        while os.path.exists(filename):
            filename = basename + "(" + str(index) + ").apd"
            index += 1

        self.current_filename = filename

        if self.compressor_args:
            if self.compressor_uses_stdout:
                with open(filename, "wb") as f:
                    process = subprocess.Popen(
                        self.compressor_args, stdin=subprocess.PIPE, stdout=f,
                        stderr=subprocess.DEVNULL, **self.popen_extras)
            else:
                args = self.compressor_args.copy()
                args.append(filename)
                process = subprocess.Popen(
                    args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, **self.popen_extras)
            self.compressor_pipe = process.stdin
            with self.compressor_lock:
                self.compressors[filename] = process
        else:
            # fall back to internal lzma module
            output = lzma.open(filename, 'wb', preset=self.compression_level)
            self.compressor_pipe = output
        self.compressor_pipe.write(self.header_bytes)

        if self.upload_pipe is not None:
            # create a .upload file to mark it for uploading
            path, name = os.path.split(filename)
            uploadfilename = os.path.join(path, "." + name + ".upload")
            with open(uploadfilename, 'w', encoding="ascii") as uploadfile:
                # Put some contents into the file. Doesn't even matter what.
                # The background scan won't touch anything with contents until
                # it's at least 20 minutes old (when the writing process is
                # presumed to have crashed).
                uploadfile.write('in progress')
            if sys.platform == "win32":
                # make the file hidden on windows
                # the leading . in the filename is enough for linux
                ctypes.windll.kernel32.SetFileAttributesW(uploadfilename, 0x02)

    def close_compressor(self):
        if self.compressor_pipe:
            self.compressor_pipe.close()
            self.compressor_pipe = None

    def mark_finished(self, filename):
        if filename:
            self.finished_queue.put(filename)

    def write(self, stream_packets):
        now = datetime.datetime.now(datetime.timezone.utc)
        self.write_queue.put((b"".join(stream_packets), now))

    def calc_next_boundary(self, dt):
        interval = 600  # 10 minutes
        seconds = ((dt.hour * 60) + dt.minute) * 60 + dt.second
        partial = datetime.timedelta(seconds=seconds % interval,
                                     microseconds=dt.microsecond)
        boundary = dt - partial + datetime.timedelta(seconds=interval)
        return boundary

    def handle_write(self, stream_packets, dt):
        if self.next_boundary is None:
            # first data point
            self.next_boundary = self.calc_next_boundary(dt)
            self.open_compressor(dt)
        elif dt > self.next_boundary:
            # passed a boundary
            finished_filename = self.current_filename
            self.close_compressor()
            self.next_boundary = self.calc_next_boundary(dt)
            self.open_compressor(dt)
            self.mark_finished(finished_filename)

        if self.compressor_pipe:
            # write the bytes
            self.compressor_pipe.write(self.packet_leader_struct.pack(
                dt.timestamp(), len(stream_packets)))
            self.compressor_pipe.write(stream_packets)

    def write_loop(self):
        try:
            last_log = time.monotonic()
            slowdown_logged = False
            while True:
                try:
                    data = self.write_queue.get(True, 0.1)

                    # less than 100 elements is "empty"
                    qsize = self.write_queue.qsize()
                    now = time.monotonic()
                    if qsize >= 100:
                        if now - last_log >= 10.0:
                            slowdown_logged = True
                            msg = "Write queue slow down: %d elements"
                            self.logger.info(msg, qsize)
                            last_log = now
                    elif qsize == 0 and slowdown_logged:
                        slowdown_logged = False
                        self.logger.info("Write queue has caught up")
                        last_log = now

                    self.handle_write(*data)
                except queue.Empty:
                    if self.is_finished.is_set():
                        break
            finished_filename = self.current_filename
            self.close_compressor()
            self.mark_finished(finished_filename)
        except Exception:
            self.logger.exception("Uncaught exception in write_loop")
        finally:
            self.write_loop_exited.set()

    def monitor_loop(self):
        try:
            while True:
                try:
                    filename = self.finished_queue.get(True, 0.1)
                    with self.compressor_lock:
                        compressor = self.compressors.get(filename)
                    if compressor:
                        # there is a compressor for this file
                        ret_val = compressor.wait()
                        if ret_val != 0:
                            msg = "Compressor exited with error {}"
                            self.logger.warning(msg.format(ret_val))
                        with self.compressor_lock:
                            del self.compressors[filename]
                    # compressor is finished (or was None, e.g. internal lzma)
                    if self.upload_pipe:
                        # empty out the .upload file
                        path, name = os.path.split(filename)
                        uploadfilename = os.path.join(path,
                                                      "." + name + ".upload")

                        # NOTE: need to use r+ then truncate() on windows
                        # because of the hidden attribute. Windows doesn't like
                        # the 'w' mode on hidden files (need different flags
                        # passed to CreateFile).
                        with open(uploadfilename, 'r+',
                                  encoding="ascii") as uploadfile:
                            uploadfile.seek(0)
                            uploadfile.truncate()

                        # send it to the uploader
                        self.upload_pipe.send(filename)
                except queue.Empty:
                    if self.write_loop_exited.is_set():
                        break
            # write loop has exited, and finished queue is empty
            with self.compressor_lock:
                for compressor in self.compressors.values():
                    ret_val = compressor.wait()
                    msg = "Uncollected compressor exited with code {}"
                    self.logger.warning(msg.format(ret_val))
                self.compressors.clear()
        except Exception:
            self.logger.exception("Uncaught exception in monitor_loop")

    def close(self):
        self.is_finished.set()

    def join(self):
        self.write_thread.join()
        self.monitor_thread.join()
        if self.upload_pipe:
            self.upload_pipe.send(None)
            self.upload_pipe.close()


class StreamManager:
    def __init__(self, device, logger, streams_to_activate, warm_up_time,
                 stream_counts, header_dict, packet_pipe, status_pipe,
                 device_name, base_dir, disable_archiving, compression_level,
                 upload_pipe):
        self.device = device
        self.logger = logger
        self.streams_to_activate = streams_to_activate
        self.warm_up_time = warm_up_time
        self.stream_counts = stream_counts
        self.header_dict = header_dict
        self.packet_pipe = packet_pipe
        self.status_pipe = status_pipe
        self.device_name = device_name
        self.base_dir = base_dir
        self.disable_archiving = disable_archiving
        self.compression_level = compression_level
        self.upload_pipe = upload_pipe

        self.got_packets = False
        self.finished = threading.Event()
        self.reset = threading.Event()

        if len(streams_to_activate) == 0:
            self.stream_thread = threading.Thread(
                target=self.stream_thread_run_no_streams)
        else:
            self.stream_thread = threading.Thread(
                target=self.stream_thread_run)

        self.writer = None

    def start(self):
        self.stream_thread.start()

    def stop(self):
        self.finished.set()

        # join the stream thread so the device can be closed
        self.stream_thread.join()
        self.status_pipe.close()
        if self.packet_pipe is not None:
            self.packet_pipe.close()

    def join(self):
        # the device has been closed at this point
        if self.writer:
            self.writer.join()
            self.writer = None

    def stream_thread_run_no_streams(self):
        try:
            if not self.disable_archiving:
                self.writer = StreamWriter(
                    self.logger, self.header_dict, self.device_name,
                    self.base_dir, self.compression_level, self.upload_pipe)

            self.status_pipe.send("connected")

            self.device.set_connect_callback(self.connect_callback)

            while True:  # loop while connected
                if self.finished.wait(timeout=0.1):
                    break

                if hyperborea.proxy.device_lock.acquire(blocking=False):
                    try:
                        # just do a meaningless test command
                        self.device.echo_params(b'')
                    except asphodel.AsphodelError:
                        self.status_pipe.send("error disconnect")
                    finally:
                        hyperborea.proxy.device_lock.release()
            self.device.set_connect_callback(None)

            # stop the writer
            if self.writer:
                self.writer.close()
        except Exception:
            self.logger.exception(
                "Unhandled exception in stream_thread_run_no_streams")
            self.status_pipe.send("error")

            # stop the writer
            if self.writer:
                self.writer.close()

    def stream_thread_run(self):
        try:
            # flush any packets already on the device
            self.flush_packets()

            if not self.disable_archiving:
                self.writer = StreamWriter(
                    self.logger, self.header_dict, self.device_name,
                    self.base_dir, self.compression_level, self.upload_pipe)

            self.device.start_streaming_packets(*self.stream_counts,
                                                callback=self.packet_callback)

            self.start_streams()

            self.status_pipe.send("connected")

            self.device.set_connect_callback(self.connect_callback)

            while not self.finished.is_set():  # loop while connected
                self.device.poll_device(100)
                if self.reset.is_set():
                    self.device.stop_streaming_packets()
                    self.device.start_streaming_packets(
                        *self.stream_counts, callback=self.packet_callback)
                    self.reset.clear()

            self.device.set_connect_callback(None)

            self.device.stop_streaming_packets()

            # do a final poll after stopping streaming to clean up
            self.device.poll_device(0)

            # stop the writer
            if self.writer:
                self.writer.close()

            try:
                self.stop_streams()
            except asphodel.AsphodelError:
                pass  # probably disconnected, ignore
        except Exception:
            self.logger.exception("Unhandled exception in stream_thread_run")
            self.status_pipe.send("error")

            # stop the writer
            if self.writer:
                self.writer.close()

    def flush_packets(self):
        stream_size = self.device.get_stream_packet_length()
        start_time = time.monotonic()
        while time.monotonic() - start_time < 0.5:
            try:
                self.device.get_stream_packets_blocking(stream_size * 10, 50)
            except asphodel.AsphodelError as e:
                if e.errno == -7:  # ASPHODEL_TIMEOUT
                    break
                else:
                    raise

    def start_streams(self):
        # warm up streams
        for stream_id in self.streams_to_activate:
            self.device.warm_up_stream(stream_id, True)

        time.sleep(self.warm_up_time)

        # enable streams
        for stream_id in self.streams_to_activate:
            self.device.enable_stream(stream_id, True)

            # disable warm up so we don't have to worry about it later
            self.device.warm_up_stream(stream_id, False)

    def stop_streams(self):
        # disable streams
        for stream_id in self.streams_to_activate:
            self.device.enable_stream(stream_id, False)

    def packet_callback(self, status, stream_packets):
        if status == -7:  # ASPHODEL_TIMEOUT
            self.status_pipe.send("error timeout")
            self.finished.set()
        elif status != 0:
            if not self.reset.is_set():
                if self.got_packets:
                    self.status_pipe.send("alert " + str(status))
                    self.got_packets = False
                    self.reset.set()
                elif not self.finished.is_set():
                    self.status_pipe.send("error " + str(status))
                    self.finished.set()
            else:
                self.status_pipe.send("extra alert " + str(status))
        else:
            self.got_packets = True
            if self.packet_pipe is not None:
                self.packet_pipe.send(stream_packets)
            if self.writer:
                self.writer.write(stream_packets)

    def connect_callback(self, status, connected):
        try:
            if not connected:
                # remove callback
                self.device.set_connect_callback(None)
                self.status_pipe.send("error disconnect")
        except Exception:
            self.logger.exception("Unhandled exception in connect_callback")
