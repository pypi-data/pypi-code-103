import itertools
import logging.handlers
import multiprocessing
import os
import queue
import signal
import sys
import threading
import traceback

import psutil
from PySide2 import QtCore

from . import namedprocess

logger = logging.getLogger(__name__)


TIMEOUT = 0.1  # 100 milliseconds

# globals
device_cleanup = {}  # key: device, value: list of (func, [args], {kwargs})
device_lock = None
subproxy_devices = {}
device_identifiers = {}  # key deivce, value: (serial_number, proxy_string)


def _simple_access(device, function_name, *args, **kwargs):
    func = getattr(device, function_name)
    result = func(*args, **kwargs)
    return result


class DeviceOperation(QtCore.QObject):
    """
    This class represents an operation on the hardware (e.g. set_leds).
    """

    completed = QtCore.Signal(object)
    error = QtCore.Signal()  # no message; that's handled by the proxy's error

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function  # function to be called in the remote process
        self.args = args  # args to pass to the function
        self.kwargs = kwargs  # kwargs to pass to the function


class SimpleDeviceOperation(DeviceOperation):
    def __init__(self, function_name, *args, **kwargs):
        super().__init__(_simple_access, function_name, *args, **kwargs)


class OptionalDeviceStringFilter:
    # creates a record.optdevice string created via fmt % record.device
    # but replaces it with fallback if record.device does not exist
    def __init__(self, fmt, fallback):
        self.fmt = fmt
        self.fallback = fallback

    def filter(self, record):
        try:
            record.optdevice = self.fmt % record.proxy_string
        except AttributeError:
            record.optdevice = self.fallback
        return True


class DeviceLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, serial_number, proxy_string=None):
        if not proxy_string:
            proxy_string = serial_number
        super().__init__(logger, {'serial_number': serial_number,
                                  "proxy_string": proxy_string})


def get_device_logger(logger, device):
    serial_number, proxy_string = device_identifiers.get(
        device, ("unknown", "unknown"))
    return DeviceLoggerAdapter(logger, serial_number, proxy_string)


def setup_remote_logging(log_queue):
    handler = logging.handlers.QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    # remove pyusb's logging info
    pyusb_logger = logging.getLogger("usb")
    pyusb_logger.propagate = False


def register_device_cleanup(device, cleanup_func, *args, **kwargs):
    cleanup_list = device_cleanup.setdefault(device, [])
    cleanup_list.append((cleanup_func, args, kwargs))


def unregister_device_cleanup(device, cleanup_func, *args, **kwargs):
    cleanup_list = device_cleanup.setdefault(device, [])
    try:
        cleanup_list.remove((cleanup_func, args, kwargs))
    except ValueError:
        pass  # was already removed


def do_device_cleanup(device):
    cleanup_list = device_cleanup.pop(device, [])
    for cleanup in cleanup_list:
        try:
            func, args, kwargs = cleanup
            func(device, *args, **kwargs)
        except Exception:
            device_logger = get_device_logger(logger, device)
            device_logger.exception("Exception during cleanup")


def do_final_cleanup(device):
    # do subproxy cleanup first
    subproxy_devices = set(device_cleanup.keys())
    subproxy_devices.discard(device)
    subproxy_devices.discard(None)
    for subproxy_device in subproxy_devices:
        do_device_cleanup(subproxy_device)

    # do device cleanup
    do_device_cleanup(device)

    # do final cleanup
    do_device_cleanup(None)


def proxy_process(log_queue, incoming, outgoing, serial_number, proxy_string,
                  find_func, ffargs, ffkwargs):
    global device_lock

    # fix a bug with stderr and stdout being None
    sys.stdout = open(os.devnull)
    sys.stderr = open(os.devnull)

    setup_remote_logging(log_queue)

    device = None
    device_lock = threading.Lock()

    # create a logger using the device specific identifier
    device_logger = DeviceLoggerAdapter(logger, serial_number, proxy_string)

    # ctrl+c handling: want to let the main process send the exit command
    if sys.platform == "win32":
        # the best way on windows? since we can't create a new process group
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    else:
        # move to a new process group (won't be signalled with ctrl+c)
        os.setpgrp()

    arg_strs = [repr(x) for x in ffargs]
    arg_strs.extend("{}={}".format(k, repr(v)) for k, v in ffkwargs.items())
    find_func_str = "{}({})".format(find_func.__name__, ", ".join(arg_strs))
    device_logger.debug("Proxy process starting with %s", find_func_str)

    me = psutil.Process(os.getpid())
    try:
        try:
            device = find_func(*ffargs, **ffkwargs)
            outgoing.put(True)  # signals success
        except Exception as e:
            device_logger.exception("Exception")
            outgoing.put(e)
        device_logger.debug("Proxy running")
        if device:
            subproxy_devices[None] = device
            device_identifiers[device] = (serial_number, proxy_string)
            while me.parent() is not None:
                try:
                    job = incoming.get(True, TIMEOUT)
                    if job is None:  # check for sentinel value
                        break
                    job_id, subproxy_id, function, args, kwargs = job
                    with device_lock:
                        proxy_device = subproxy_devices[subproxy_id]
                        proxy_logger = get_device_logger(logger, proxy_device)
                        proxy_logger.debug("got: {}".format(job))
                        try:
                            result = function(proxy_device, *args, **kwargs)
                            outgoing_tuple = (job_id, result, None)
                            msg = "finished: {} => {}".format(job, result)
                            proxy_logger.debug(msg)
                        except Exception as e:
                            proxy_logger.exception("Exception")
                            outgoing_tuple = (job_id, None, e)
                        outgoing.put(outgoing_tuple)
                except queue.Empty:
                    pass

        # finished with the outgoing queue
        outgoing.put(None)  # sentinel value
        outgoing.close()

        if device:
            with device_lock:
                do_final_cleanup(device)
    except Exception:
        device_logger.exception("Uncaught Exception in Remote Process")
        raise
    finally:
        if device:
            device.close()
    device_logger.debug("Proxy process ending")


class DeviceProxy(QtCore.QObject):
    """
    This class represents a Device being handled in a different process.
    """

    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    error = QtCore.Signal(str)

    def __init__(self, process_name, log_queue, serial_number, proxy_string,
                 find_func, *args, **kwargs):
        super().__init__()
        self.serial_number = serial_number
        self.proxy_string = proxy_string
        self.log_queue = log_queue

        self.logger = DeviceLoggerAdapter(logger, serial_number, proxy_string)

        self.toProcess = multiprocessing.Queue()
        self.fromProcess = multiprocessing.Queue()

        self.process = namedprocess.NamedProcess(
            name=process_name, description=serial_number, target=proxy_process,
            args=(self.log_queue, self.toProcess, self.fromProcess,
                  serial_number, proxy_string, find_func, args, kwargs))
        self.process.daemon = True

        self.monitor_thread = threading.Thread(target=self.monitor)
        self.started = False

        self.jobs = {}
        self.next_job_index = 0

        self.subproxy_id_counter = itertools.count()

    def handle_exception(self, proxy, exc):
        m = traceback.format_exception_only(type(exc), exc)
        message = "".join(m)

        # trim any trailing newline
        if message[-1:] == "\n":
            message = message[:-1]

        # already logged in the proxy process
        # proxy.logger.error(message)

        proxy.error.emit(message)
        proxy.close_connection()

    def handle_reply(self, reply):
        try:
            if reply is True:  # connection success
                self.connected.emit()
            elif isinstance(reply, Exception):
                self.handle_exception(self, reply)
            else:
                job_id, result, exc = reply
                operation, proxy = self.jobs.pop(job_id)
                if exc is None:
                    if result is None:  # NOTE: emitting None will crash pyside
                        result = type(None)  # send builtins.NoneType instead
                    operation.completed.emit(result)
                else:
                    self.handle_exception(proxy, exc)
                    operation.error.emit()
        except Exception:
            self.logger.exception("Unhandled Exception in Monitor Thread")

    def monitor(self):
        """
        thread target to monitor the responses from the remote process
        """
        self.logger.debug("Monitor thread starting")
        self.started = True
        normal_exit = False
        while self.process.is_alive():  # check that process is still running
            try:
                reply = self.fromProcess.get(True, TIMEOUT)
                if reply is None:  # check for sentinel value
                    normal_exit = True
                    break
                self.handle_reply(reply)
            except queue.Empty:
                pass
        # might still be entries in the queue
        while True:
            try:
                reply = self.fromProcess.get(False)
                if reply is None:
                    normal_exit = True
                    continue
                self.handle_reply(reply)
            except queue.Empty:
                break
        for operation, _proxy in list(self.jobs.values()):
            operation.error.emit()
        self.jobs = {}  # empty out the jobs
        self.logger.debug("Monitor thread finished")
        if not normal_exit:
            message = "Device Process Closed Prematurely!"
            self.logger.error(message)
            self.error.emit(message)
        self.disconnected.emit()
        self.process.join()
        self.logger.debug("Monitor thread closing")

    @QtCore.Slot()
    def open_connection(self):
        if self.monitor_thread.is_alive() or self.process.is_alive():
            raise Exception("Proxy already opened!")
        self.process.start()
        self.monitor_thread.start()
        # NOTE: connected is emitted when the device connection is established

    @QtCore.Slot()
    def close_connection(self):
        self.toProcess.put(None)  # send sentinel value to remote process
        # NOTE: monitor waits for process to finish then emits disconnected

    def send_job(self, operation, *args, proxy=None, **kwargs):
        if proxy is None:
            proxy = self
            subproxy_id = None
        else:
            subproxy_id = proxy.subproxy_id

        job_index = self.next_job_index
        self.next_job_index = (self.next_job_index + 1) & 0xFFFFFFFF
        self.jobs[job_index] = (operation, proxy)

        new_kwargs = dict(list(operation.kwargs.items()) +
                          list(kwargs.items()))
        new_args = operation.args + args

        self.toProcess.put((job_index, subproxy_id, operation.function,
                            new_args, new_kwargs))

    def wait_for_close(self):
        if self.monitor_thread.is_alive():
            self.close_connection()
            self.monitor_thread.join()
        QtCore.QCoreApplication.processEvents()

    def is_finished(self):
        if self.started:
            return not self.monitor_thread.is_alive()
        else:
            return False

    def create_subproxy(self, func, *args, **kwargs):
        subproxy_id = next(self.subproxy_id_counter)
        op = DeviceOperation(create_subproxy_util, func, subproxy_id,
                             self.proxy_string, *args, **kwargs)
        subproxy = DeviceSubProxy(self, subproxy_id, op)
        return subproxy


def create_subproxy_util(device, func, subproxy_id, proxy_string,
                         *args, **kwargs):
    """ called from create_subproxy() to handle registration """
    try:
        subproxy_device = func(device, *args, **kwargs)
        subproxy_devices[subproxy_id] = subproxy_device

        subproxy_sn = subproxy_device.get_serial_number()
        subproxy_string = "{}->{}".format(proxy_string, subproxy_sn)
        device_identifiers[subproxy_device] = (subproxy_sn, subproxy_string)

        return (True, subproxy_sn, subproxy_string)
    except Exception:
        get_device_logger(logger, device).exception(
            "Unhandled exception in create_subproxy_util()")
        return (False, None, None)


class DeviceSubProxy(QtCore.QObject):

    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    error = QtCore.Signal(str)

    def __init__(self, proxy, subproxy_id, start_op):
        super().__init__()

        self.proxy = proxy
        self.logger = proxy.logger  # temporary until we get a new one
        self.subproxy_id = subproxy_id
        self.start_op = start_op

        self.opened = False

        # connect signals from the parent into this instance
        self.proxy.disconnected.connect(self.disconnected)
        self.proxy.error.connect(self.error)

        self.close_job = DeviceOperation(do_device_cleanup)
        self.close_job.completed.connect(self.close_completed)

    @QtCore.Slot()
    def open_connection(self):
        self.start_op.completed.connect(self.connected_cb)
        self.proxy.send_job(self.start_op)
        # NOTE: connected is emitted when the device connection is established

    @QtCore.Slot()
    def close_connection(self):
        if self.opened:
            self.proxy.send_job(self.close_job, proxy=self)
            self.opened = False

    def close_completed(self):
        self.proxy.disconnected.disconnect(self.disconnected)
        self.proxy.error.disconnect(self.error)
        self.disconnected.emit()

    def connected_cb(self, result):
        success, serial_number, subproxy_string = result
        if success:
            self.logger = DeviceLoggerAdapter(logger, serial_number,
                                              subproxy_string)
            self.opened = True
            self.connected.emit()
        else:
            self.error.emit("Subproxy Creation Failed")
            self.proxy.disconnected.disconnect(self.disconnected)
            self.proxy.error.disconnect(self.error)
            self.disconnected.emit()

    def wait_for_close(self):
        pass

    def send_job(self, operation, *args, **kwargs):
        if self.opened:
            self.proxy.send_job(operation, *args, proxy=self,
                                **kwargs)


class RemoteToLocalLogHandler(logging.Handler):
    def __init__(self, logger_name):
        super().__init__()
        self.logger = logging.getLogger(logger_name)

    def emit(self, record):
        self.logger.handle(record)


class DeviceProxyManager:
    def __init__(self, process_name):
        self.process_name = process_name
        self.setup_logging()
        self.proxies = []
        self.next_proxy_number = 0

    def setup_logging(self):
        local_handler = RemoteToLocalLogHandler(__name__ + ".remote")

        self.logQueue = multiprocessing.Queue()
        self.logListener = logging.handlers.QueueListener(
            self.logQueue, local_handler)
        self.logListener.start()

    def stop(self):
        for proxy in self.proxies:
            proxy.wait_for_close()
        self.logListener.stop()

    def clear_finished_proxies(self):
        original_proxies = self.proxies
        for proxy in original_proxies:
            if proxy.is_finished():
                self.proxies.remove(proxy)

    def new_proxy(self, serial_number, find_func, *args, **kwargs):
        # clear finished proxies first
        self.clear_finished_proxies()

        proxy_number = self.next_proxy_number
        self.next_proxy_number += 1

        proxy_string = "{}:{}".format(proxy_number, serial_number)

        proxy = DeviceProxy(self.process_name, self.logQueue, serial_number,
                            proxy_string, find_func, *args, **kwargs)
        self.proxies.append(proxy)
        return proxy
