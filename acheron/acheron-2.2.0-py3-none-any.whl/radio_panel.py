import bisect
import collections
import enum
import datetime
import functools
import logging
import multiprocessing
import time
import threading

from PySide2 import QtCore, QtGui, QtWidgets

import asphodel
import hyperborea.proxy

from . import bootloader
from . import detail_scan
from .bulk_update_firmware import BulkUpdateFirmwareDialog
from .ui_radio_panel import Ui_RadioPanel

logger = logging.getLogger(__name__)


instances = {}


ScanResult = collections.namedtuple(
    "ScanResult", ["serial_number", "is_bootloader", "asphodel_type",
                   "device_mode", "scan_strength"])


def start_radio_manager(device, *args, **kwargs):
    device_logger = hyperborea.proxy.get_device_logger(logger, device)
    device_logger.debug("Starting radio manager")

    if device in instances:
        stop_radio_manager(device)

    instance = RadioManager(device, device_logger, *args, **kwargs)
    instances[device] = instance
    instance.start()

    hyperborea.proxy.register_device_cleanup(device, stop_radio_manager)


def stop_radio_manager(device):
    if device not in instances:
        return

    instances[device].stop()

    device_logger = hyperborea.proxy.get_device_logger(logger, device)
    device_logger.debug("Stopped radio manager")

    del instances[device]

    hyperborea.proxy.unregister_device_cleanup(device, stop_radio_manager)


def create_remote(device):
    return instances[device].get_remote()


@enum.unique
class RadioManagerState(enum.Enum):
    IDLE = 0
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECTING = 3


class RadioManager:
    def __init__(self, device, logger, diskcache, status_pipe, control_pipe,
                 supports_scan_power):
        self.device = device
        self.logger = logger
        self.diskcache = diskcache
        self.status_pipe = status_pipe
        self.control_pipe = control_pipe

        self.remote = device.get_remote_device()
        self.remote_users = 0

        self.state = RadioManagerState.IDLE
        self.first_pass = True
        self.last_connect = None  # (sn, is_boot)

        self.supports_scan_power = supports_scan_power
        self.power_max_queries = min(
            self.device.get_max_outgoing_param_length() // 4,
            self.device.get_max_incoming_param_length())

        self.active_scans = collections.deque()

        self.finished = threading.Event()
        self.manager_thread = threading.Thread(target=self.manager_thread_run)

    def start(self):
        self.manager_thread.start()
        self.remote.open()

    def stop(self):
        self.finished.set()

        # note: need to release the lock while waiting for the thread to finish
        hyperborea.proxy.device_lock.release()
        self.manager_thread.join()
        hyperborea.proxy.device_lock.acquire()

        self.remote.close()
        self.status_pipe.close()
        self.control_pipe.close()

    def get_remote(self):  # called with device_lock
        self.logger.debug("Claiming remote")

        self.remote.open()
        self.remote.flush()

        # set up a clean up function
        hyperborea.proxy.register_device_cleanup(
            self.remote, self.clean_up_remote)
        self.remote_users += 1

        return self.remote

    def clean_up_remote(self, _remote):  # called with device_lock
        self.remote_users -= 1
        if self.remote_users == 0:
            self.logger.debug("Releasing remote")
            try:
                self.device.stop_radio()
                self.remote.open()
                self.remote.flush()
            except Exception:
                pass  # ignore for now, probably in the process of closing
            self.state = RadioManagerState.IDLE
            self.first_pass = True
        else:
            self.logger.debug("Releasing remote, but still claimed")

    def process_control_pipe(self):  # NOT called with device_lock
        while True:
            try:
                pipe_ready = self.control_pipe.poll()
            except Exception:
                # pipe broken
                self.finished.set()
                return
            if pipe_ready:
                try:
                    request = self.control_pipe.recv()
                    if request[0] == "active scan":
                        self.active_scans.append(request[1:])
                    elif request[0] == "connect":
                        with hyperborea.proxy.device_lock:
                            self.remote.open()  # just in case
                            self.start_connect(*request[1:])
                    elif request[0] == "disconnect":
                        with hyperborea.proxy.device_lock:
                            self.start_disconnect()
                    elif request[0] == "function":
                        with hyperborea.proxy.device_lock:
                            # treat this like a disconnect
                            self.start_disconnect()

                            self.logger.debug("Starting radio function")

                            # do the function
                            func = request[1]
                            func(self.device, self.remote, *request[2:])
                            self.status_pipe.send(("function",))
                except EOFError:
                    # pipe broken, treat it like a stop call
                    self.finished.set()
                    return
            else:
                break

    def check_idle(self):  # called with device_lock
        if self.finished.is_set():
            raise StopIteration()
        try:
            pipe_ready = self.control_pipe.poll(0.001)
        except Exception:
            # pipe broken
            self.finished.set()
            raise StopIteration()
        if pipe_ready:
            raise StopIteration()

    def start_connect(self, serial, is_bootloader):  # called with device_lock
        if not is_bootloader:
            self.logger.debug("Starting connect to %s", serial)
            self.device.connect_radio(serial)
        else:
            self.logger.debug("Starting bootloader connect to %s", serial)
            self.device.connect_radio_boot(serial)
        self.last_connect = (serial, is_bootloader)
        self.state = RadioManagerState.CONNECTING

    def start_disconnect(self):  # called with device_lock
        self.logger.debug("Starting disconnect")
        if self.remote_users == 0:
            self.device.stop_radio()
            self.remote.open()
            self.state = RadioManagerState.IDLE
            self.first_pass = True
        else:
            self.state = RadioManagerState.DISCONNECTING

    def do_active_scan(self, serial, is_bootloader):
        with hyperborea.proxy.device_lock:
            try:
                if not is_bootloader:
                    self.logger.debug("Starting active scan on %s", serial)
                    self.device.connect_radio(serial)
                else:
                    self.logger.debug("Starting bootloader active scan on %s",
                                      serial)
                    self.device.connect_radio_boot(serial)

                self.remote.wait_for_connect(1000)

                device_info = hyperborea.device_info.get_active_scan_info(
                    self.device, self.remote, self.diskcache)
                last_seen = datetime.datetime.now(datetime.timezone.utc)
                self.logger.debug("Finished active scan on %s", serial)
            except Exception:
                # couldn't do the active scan
                # no big deal
                device_info = None
                last_seen = None
                self.logger.debug("Failed active scan on %s", serial)
            finally:
                self.device.stop_radio()
        self.status_pipe.send(("active scan", serial, device_info, last_seen))

    def collect_scan_results(self, is_bootloader):  # called with device_lock
        last_seen = datetime.datetime.now(datetime.timezone.utc)

        # get the results
        results = self.device.get_radio_extra_scan_results()

        # get the scan powers
        scan_powers = {}  # key: sn, value: power dBm
        if self.supports_scan_power:
            for i in range(0, len(results), self.power_max_queries):
                result_subset = results[i:i + self.power_max_queries]
                serials = [r.serial_number for r in result_subset]
                powers = self.device.get_radio_scan_power(serials)
                for sn, power in zip(serials, powers):
                    if power != 0x7F:
                        scan_powers[sn] = power

        for r in results:
            power = scan_powers.get(r.serial_number, None)
            is_bootloader = bool(r.asphodel_type &
                                 asphodel.ASPHODEL_PROTOCOL_TYPE_BOOTLOADER)
            s = ScanResult(r.serial_number, is_bootloader, r.asphodel_type,
                           r.device_mode, power)
            self.status_pipe.send(("scan", s, last_seen))

    def do_scan(self):
        with hyperborea.proxy.device_lock:
            try:
                self.device.start_radio_scan()
                end_time = time.monotonic() + 0.6  # 600 ms
                while time.monotonic() < end_time:
                    self.collect_scan_results(is_bootloader=False)
                    self.check_idle()
            finally:
                self.device.stop_radio()

    def do_bootloader_scan(self):
        with hyperborea.proxy.device_lock:
            try:
                self.device.start_radio_scan_boot()
                end_time = time.monotonic() + 0.1  # 100 ms
                while time.monotonic() < end_time:
                    self.collect_scan_results(is_bootloader=True)
                    self.check_idle()
            finally:
                self.device.stop_radio()

    def manager_thread_run(self):
        try:
            while not self.finished.is_set():
                self.process_control_pipe()

                if self.state == RadioManagerState.CONNECTING:
                    with hyperborea.proxy.device_lock:
                        status = self.device.get_radio_status()
                        connected = status[0]
                        serial_number = status[1]

                        if connected:
                            sn_str = self.remote.get_serial_number()
                            if sn_str:
                                self.state = RadioManagerState.CONNECTED
                                self.status_pipe.send(
                                    ("connected", serial_number, sn_str))
                            else:
                                # immediate disconnect, start again
                                self.start_connect(*self.last_connect)
                        elif serial_number == 0:
                            # immediate disconnect, start again
                            self.start_connect(*self.last_connect)
                    # check status
                elif self.state == RadioManagerState.IDLE:
                    try:
                        self.do_scan()
                        self.do_bootloader_scan()

                        if self.first_pass:
                            self.first_pass = False
                            self.status_pipe.send(("first pass",))

                        try:
                            serial, is_bootloader = self.active_scans.popleft()
                            self.do_active_scan(serial, is_bootloader)
                        except IndexError:
                            pass
                    except StopIteration:
                        continue
                else:
                    # don't need to be doning other things, sleep for a bit
                    self.finished.wait(timeout=0.1)
        except Exception:
            self.logger.exception("Unhandled exception in manager_thread_run")
            try:
                self.status_pipe.send(("error",))
            except Exception:
                pass
        finally:
            try:
                with hyperborea.proxy.device_lock:
                    self.remote.close()
                    self.device.stop_radio()
            except Exception:
                pass  # device probably disconnected


def bulk_claim(device, remote):
    device_logger = hyperborea.proxy.get_device_logger(logger, device)

    try:
        to_claim = set()

        device.start_radio_scan()
        finish = time.monotonic() + 1
        while finish > time.monotonic():
            for result in device.get_radio_extra_scan_results():
                if result.device_mode:
                    to_claim.add(result.serial_number)
        device.stop_radio()

        if not to_claim:
            device_logger.info("No Devices to Claim")
        else:
            for serial_number in to_claim:
                try:
                    device_logger.info("Claiming %s...", serial_number)
                    device.connect_radio(serial_number)
                    remote.wait_for_connect(5000)
                    remote.set_device_mode(0)
                    device_logger.info("Claimed %s", serial_number)
                except Exception:
                    device_logger.error("Error Claiming %s", serial_number)
            device_logger.info("Finished Bulk Claim")
    finally:
        device.stop_radio()
        remote.close()


class PipeWithSerial:  # for bulk_update
    def __init__(self, pipe):
        self.pipe = pipe
        self.serial_number = 0

    def send(self, message):
        if isinstance(message, str):
            new_message = "{}: {}".format(self.serial_number, message)
            self.pipe.send(new_message)
        else:
            self.pipe.send(message)

    def close(self):
        # ignore close calls, the pipe will be reused
        pass


def bulk_update(device, remote, progress_pipe, cancel_pipe, firm_data,
                valid_range, device_mode, radio_strength):
    canceled = False
    pipe_with_serial = PipeWithSerial(progress_pipe)
    device_logger = hyperborea.proxy.get_device_logger(logger, device)

    power_max_queries = min(device.get_max_outgoing_param_length() // 4,
                            device.get_max_incoming_param_length())

    scanned = 0
    to_program = 0
    ignored = 0
    finished = 0
    errors = 0

    try:
        # all of these contain elements of (sn, app_mode)
        unknown_serials = set()
        reprogram_serials = set()

        scan_powers = {}  # key: sn, value: power dBm

        progress_pipe.send("Scanning for bootloaders...")
        device.start_radio_scan_boot()
        finish = time.monotonic() + 1  # 1 second
        while finish > time.monotonic():
            unknown_powers = []
            for result in device.get_radio_extra_scan_results():
                if result.serial_number in valid_range:
                    unknown_serials.add((False, result.serial_number))
                    if result.serial_number not in scan_powers:
                        unknown_powers.append(result.serial_number)
            # get the powers
            if radio_strength is not None:
                for i in range(0, len(unknown_powers), power_max_queries):
                    serials = unknown_powers[i:i + power_max_queries]
                    powers = device.get_radio_scan_power(serials)
                    for sn, power in zip(serials, powers):
                        if power != 0x7F:
                            scan_powers[sn] = power
        device.stop_radio()

        progress_pipe.send("Scanning for devices...")
        device.start_radio_scan()
        finish = time.monotonic() + 2  # 2 seconds
        while finish > time.monotonic():
            unknown_powers = []
            for result in device.get_radio_extra_scan_results():
                if result.serial_number in valid_range:
                    unknown_serials.add((True, result.serial_number))
                    if result.serial_number not in scan_powers:
                        unknown_powers.append(result.serial_number)
            # get the powers
            if radio_strength is not None:
                for i in range(0, len(unknown_powers), power_max_queries):
                    serials = unknown_powers[i:i + power_max_queries]
                    powers = device.get_radio_scan_power(serials)
                    for sn, power in zip(serials, powers):
                        if power != 0x7F:
                            scan_powers[sn] = power
        device.stop_radio()

        # filter by radio strength
        if radio_strength is not None:
            for app_mode, serial_number in unknown_serials.copy():
                if serial_number in scan_powers:
                    if scan_powers[serial_number] < radio_strength:
                        unknown_serials.remove((app_mode, serial_number))

        if not unknown_serials:
            device_logger.info("No Devices Found")
            return

        scanned = len(unknown_serials)

        for app_mode, serial_number in sorted(unknown_serials):
            try:
                # connect
                progress_pipe.send("Querying {}...".format(serial_number))
                if app_mode:
                    device.connect_radio(serial_number)
                else:
                    device.connect_radio_boot(serial_number)
                remote.wait_for_connect(5000)

                if app_mode and remote.get_bootloader_info() != "Asphodel":
                    device_logger.info(
                        "{} doesn't have a bootloader".format(serial_number))
                    continue

                # see if the firmware is supported
                board_info = remote.get_board_info()
                for rev, board_name in firm_data['board']:
                    if (rev == board_info[1] and
                            board_name == board_info[0]):
                        break
                else:
                    device_logger.info("{} isn't a supported board".format(
                        serial_number))
                    continue

                if firm_data['chip'] != remote.get_chip_model():
                    device_logger.info("{} doesn't have correct chip".format(
                        serial_number))
                    continue

                in_bootloader = remote.supports_bootloader_commands()
                device_info = {'supports_bootloader': in_bootloader,
                               'build_info': remote.get_build_info(),
                               'build_date': remote.get_build_date()}
                if bootloader.already_programmed(firm_data, device_info):
                    device_logger.info("{} already programmed".format(
                        serial_number))
                    continue

                reprogram_serials.add((app_mode, serial_number))
            except Exception:
                device_logger.info("Error Querying {}".format(serial_number))

        if not reprogram_serials:
            device_logger.info("No Valid Devices Found")
            return

        to_program = len(reprogram_serials)
        ignored = scanned - to_program

        device_logger.info(
            "Bulk Update: scanned=%s, ignored=%s, to_program=%s", scanned,
            ignored, to_program)

        for app_mode, serial_number in sorted(reprogram_serials):
            if cancel_pipe.poll():
                progress_pipe.send("Cancelling...")
                canceled = True
                break

            try:
                tries = 2
                while True:
                    try:
                        # connect
                        progress_pipe.send((0, 0))
                        progress_pipe.send("Connecting to {}...".format(
                            serial_number))
                        if app_mode:
                            device.connect_radio(serial_number)
                        else:
                            device.connect_radio_boot(serial_number)
                        remote.wait_for_connect(5000)

                        # bootloader
                        pipe_with_serial.serial_number = serial_number
                        bootloader.do_bootload(remote, firm_data,
                                               pipe_with_serial)

                        # device mode
                        if device_mode is not None:
                            remote.set_device_mode(device_mode)
                    except Exception:
                        tries -= 1
                        if tries == 0:
                            raise
                        else:
                            continue
                    break
                finished += 1
                device_logger.info("Finished {}".format(serial_number))
            except Exception:
                errors += 1
                device_logger.exception("Error Programming {}".format(
                    serial_number))
    finally:
        progress_pipe.close()
        device.stop_radio()
        remote.close()

    device_logger.info(
        "Bulk Update: scanned=%s, ignored=%s, finished=%s, errors=%s", scanned,
        ignored, finished, errors)

    if canceled:
        device_logger.info("Canceled Bulk Update")
    else:
        device_logger.info("Finished Bulk Update")


class ActiveScanDatabase(QtCore.QObject):
    clear = QtCore.Signal()
    scan_result_ready = QtCore.Signal(object, object)
    update_connected_radio = QtCore.Signal(object, object)

    def __init__(self):
        super().__init__()

        self.lock = threading.Lock()
        self.ongoing_active_scans = set()
        self.connected_devices = set()  # serial numbers
        self.connected_panels = {}  # key: panel, value: sn

        self.active_scans = {}
        self.regular_scans = {}

    def active_scan_finished(self, serial_number, device_info):
        with self.lock:
            self.ongoing_active_scans.discard(serial_number)

            if device_info:
                self.active_scans[serial_number] = device_info

        if device_info:
            self.scan_result_ready.emit(serial_number, device_info)

    def get_scan_info(self, serial_number):
        with self.lock:
            return self.active_scans.get(serial_number)

    def should_start_active_scan(self, serial_number):
        with self.lock:
            if serial_number in self.active_scans:
                # already have it
                return False

            if serial_number in self.ongoing_active_scans:
                # someone already doing the scan
                return False

            if serial_number in self.connected_devices:
                return False

            self.ongoing_active_scans.add(serial_number)
            return True

    def clear_database(self):
        with self.lock:
            self.active_scans.clear()
            self.regular_scans.clear()
            self.ongoing_active_scans.clear()

        self.clear.emit()

    def clear_entry(self, serial_number):
        with self.lock:
            self.active_scans.pop(serial_number, None)
            self.ongoing_active_scans.discard(serial_number)
        self.scan_result_ready.emit(serial_number, {})

    def regular_scan_ready(self, scan):
        with self.lock:
            old_scan = self.regular_scans.get(scan.serial_number)
            self.regular_scans[scan.serial_number] = scan

        if old_scan:
            # see if then device has changed in any noticable way
            if (old_scan.is_bootloader != scan.is_bootloader or
                    old_scan.asphodel_type != scan.asphodel_type or
                    old_scan.device_mode != scan.device_mode):
                self.clear_entry(scan.serial_number)

    def _get_panel_radio_name(self, panel):
        return panel.device_tab.serial_number

    def update_connected(self, radio_panel, serial_number):
        with self.lock:
            old_sn = self.connected_panels.pop(radio_panel, None)
            self.connected_panels[radio_panel] = serial_number

            self.connected_devices = set(self.connected_panels.values())

            old_removed = old_sn and old_sn not in self.connected_devices
            if old_removed:
                # just in case
                self.ongoing_active_scans.discard(old_sn)

        if old_removed:
            # old_sn no longer connected
            self.update_connected_radio.emit(old_sn, "")

        if serial_number:
            # serial number now connected
            connected_radio = self._get_panel_radio_name(radio_panel)
            self.update_connected_radio.emit(serial_number, connected_radio)

    def get_connected_radio(self, serial_number):
        with self.lock:
            if serial_number not in self.connected_devices:
                return None
            else:
                for radio_panel, sn in self.connected_panels.items():
                    if sn == serial_number:
                        return self._get_panel_radio_name(radio_panel)
                raise KeyError()


active_scan_database = None  # initialized once, then reused


@enum.unique
class RadioPanelState(enum.Enum):
    STOPPED = 0
    IDLE = 1
    CONNECTING = 2
    CONNECTED = 3
    RUNNING_FUNCTION = 4


class RadioPanel(QtWidgets.QGroupBox, Ui_RadioPanel):
    status_received = QtCore.Signal(object)

    def __init__(self, start_proxy_operation, diskcache, parent=None):
        super().__init__(parent)

        self.diskcache = diskcache
        self.device_tab = parent
        self.logger = parent.logger
        self.start_proxy_operation = start_proxy_operation
        self.finish_function = None

        self.active_scan_serial = None
        global active_scan_database
        if not active_scan_database:
            active_scan_database = ActiveScanDatabase()

        self.state = None
        self.remote_tab = None

        self.streaming = True
        self.connecting_scan = None

        self.temporary_scan = None  # a placeholder scan in the list
        self.scan_serials = []
        self.scans = []
        self.default_serial = 0
        self.last_seen = {}  # key: sn, value: last_seen
        self.device_list_additions = collections.deque()

        self.stopped = threading.Event()
        self.rx_status_pipe = None
        self.tx_status_pipe = None
        self.rx_control_pipe = None
        self.tx_control_pipe = None

        self.setupUi(self)
        self.extra_ui_setup()
        self.setup_callbacks()
        self.setup_proxy_operations()
        self.set_ui_state(RadioPanelState.STOPPED)

    def extra_ui_setup(self):
        self.detail_scan_dialog = detail_scan.DetailScanDialog(self)

        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.actionConnectNoStreaming)
        self.menu.addSeparator()
        self.menu.addAction(self.actionBulkClaim)
        self.menu.addAction(self.actionBulkUpdateFirmware)
        self.menu.addSeparator()
        self.menu.addAction(self.actionConnectAnyBootloader)
        self.menu.addAction(self.actionConnectSpecificBootloader)
        self.menu.addAction(self.actionConnectSpecificSerial)
        self.advancedMenuButton.setMenu(self.menu)

        self.deviceList.addAction(self.actionClear)

        self.bulk_update_progress = QtWidgets.QProgressDialog(
            self.tr(""), self.tr("Cancel"), 0, 100)
        self.bulk_update_progress.setWindowTitle(self.tr("Bulk Update"))
        self.bulk_update_progress.setWindowModality(QtCore.Qt.WindowModal)
        self.bulk_update_progress.setMinimumDuration(0)
        self.bulk_update_progress.setAutoReset(False)
        self.bulk_update_progress.canceled.connect(self.bulk_update_canceled)
        self.bulk_update_progress.reset()

        self.actionClear.setIcon(QtGui.QIcon.fromTheme("delete"))
        self.clearButton.setDefaultAction(self.actionClear)

    def setup_callbacks(self):
        self.status_received.connect(self.status_callback)

        self.detailScanButton.clicked.connect(self.detail_scan)

        self.connectButton.clicked.connect(self.connect_button_cb)
        self.disconnectButton.clicked.connect(self.disconnect_button_cb)
        self.goToRemoteButton.clicked.connect(self.show_remote_tab)

        self.deviceList.currentRowChanged.connect(self.current_row_changed_cb)
        self.deviceList.itemDoubleClicked.connect(self.item_double_clicked_cb)

        self.actionConnectNoStreaming.triggered.connect(
            self.connect_no_streaming_cb)
        self.actionConnectAnyBootloader.triggered.connect(
            self.connect_any_bootloader_cb)
        self.actionConnectSpecificBootloader.triggered.connect(
            self.connect_specific_bootloader_cb)
        self.actionConnectSpecificSerial.triggered.connect(
            self.connect_specific_serial_cb)
        self.actionBulkClaim.triggered.connect(self.start_bulk_claim)
        self.actionBulkUpdateFirmware.triggered.connect(
            self.start_bulk_update_firmware)
        self.actionClear.triggered.connect(self.clear_list)

        self.bulk_update_progress_timer = QtCore.QTimer(self)
        self.bulk_update_progress_timer.timeout.connect(
            self.bulk_update_progress_cb)

        active_scan_database.clear.connect(self.update_device_list)

        self.update_device_list_timer = QtCore.QTimer(self)
        self.update_device_list_timer.timeout.connect(
            self.update_device_list)
        self.update_device_list_timer.start(250)

    def setup_proxy_operations(self):
        self.start_radio_manager_op = hyperborea.proxy.DeviceOperation(
            start_radio_manager)
        self.stop_radio_manager_op = hyperborea.proxy.DeviceOperation(
            stop_radio_manager)
        self.stop_radio_manager_op.completed.connect(
            self.stop_radio_manager_cb)

    def add_ctrl_var_widget(self, widget):  # called from device_tab
        self.ctrlVarLayout.addWidget(widget)

    def connected(self, device_info):  # called from device_tab
        if self.state != RadioPanelState.STOPPED:
            return  # ignore

        self.supports_scan_power = device_info['radio_scan_power']

        rx, tx = multiprocessing.Pipe(False)
        self.rx_status_pipe = rx
        self.tx_status_pipe = tx
        rx, tx = multiprocessing.Pipe(False)
        self.rx_control_pipe = rx
        self.tx_control_pipe = tx
        self.start_proxy_operation(
            self.start_radio_manager_op, self.diskcache, self.tx_status_pipe,
            self.rx_control_pipe, self.supports_scan_power)

        self.stopped.clear()
        self.status_thread = threading.Thread(target=self.status_thread_run)
        self.status_thread.start()

        self.default_serial = device_info['radio_default_serial'] & 0xFFFFFFFF
        if self.default_serial == 0:
            self.set_ui_state(RadioPanelState.IDLE)
        else:
            scan = ScanResult(self.default_serial, False, 0, 0, None)
            self.set_selected_scan(scan)  # make it permanent
            self.start_connect(scan)

    def disconnected(self):  # called from device_tab
        # the device has been disconnected (e.g. unplugged)

        if self.state != RadioPanelState.STOPPED:
            self.close_remote_tab()
            self.start_proxy_operation(self.stop_radio_manager_op)

            self.set_ui_state(RadioPanelState.STOPPED)

            if self.active_scan_serial is not None:
                active_scan_database.active_scan_finished(
                    self.active_scan_serial, None)
                self.active_scan_serial = None

            active_scan_database.update_connected(self, None)

    def stop(self):  # called from device_tab
        self.disconnected()

    def status_thread_run(self):
        pipe = self.rx_status_pipe
        while True:
            # check if should exit
            if self.stopped.is_set():
                break

            if pipe.poll(0.1):  # 100 ms
                try:
                    data = pipe.recv()
                except EOFError:
                    break

                # send the data to status_callback()
                self.status_received.emit(data)

    def stop_radio_manager_cb(self):
        self.stopped.set()
        self.status_thread.join()
        self.rx_status_pipe.close()
        self.tx_control_pipe.close()
        self.rx_status_pipe = None
        self.tx_status_pipe = None
        self.rx_control_pipe = None
        self.tx_control_pipe = None

    def status_callback(self, status):
        if status[0] == "connected":
            serial_number, sn_str = status[1:]

            if self.connecting_scan.serial_number != serial_number:
                new_scan = ScanResult(serial_number, *self.connecting_scan[1:])
                self.connecting_scan = new_scan
                self.set_selected_scan(new_scan)

            subproxy = self.device_tab.proxy.create_subproxy(create_remote)
            cb = functools.partial(self.subproxy_connected_cb, subproxy,
                                   sn_str)
            subproxy.connected.connect(cb)
            subproxy.disconnected.connect(self.reconnect)
            subproxy.open_connection()
        elif status[0] == "scan":
            self.handle_scan(*status[1:])
        elif status[0] == "active scan":
            self.handle_active_scan(*status[1:])
        elif status[0] == "function":
            self.set_ui_state(RadioPanelState.IDLE)
        elif status[0] == "first pass":
            self.handle_device_list_additions()
            if self.get_selected_scan() is None:
                if self.deviceList.count():
                    self.deviceList.setCurrentRow(0)
        elif status[0] == "error":
            self.logger.error("Radio manager closed unexpectedly")
            self.disconnected()

    def subproxy_connected_cb(self, subproxy, sn_str):
        # the remote tab disconnected_signal will be used instead
        subproxy.disconnected.disconnect(self.reconnect)

        if self.state not in (RadioPanelState.CONNECTED,
                              RadioPanelState.CONNECTING):
            subproxy.close_connection()

        self.logger.info("Connected to {}".format(sn_str))

        if self.remote_tab:
            self.remote_tab.set_proxy(subproxy)
            self.set_ui_state(RadioPanelState.CONNECTED)
        else:
            self.remote_tab = self.device_tab.plotmain.create_tab(
                subproxy, sn_str, True if self.streaming else [])

            # make a reference to this tab so the remote panel can function
            self.remote_tab.radio_tab = self.device_tab

            # have the remote's close button act like a disconnect press
            self.remote_tab.close_pressed.connect(self.disconnect_button_cb)

            # reconnect when it disconnects
            self.remote_tab.disconnected_signal.connect(self.reconnect)

            self.set_ui_state(RadioPanelState.CONNECTED)
            self.show_remote_tab()

    def reconnect(self):
        if self.state in (RadioPanelState.CONNECTED,
                          RadioPanelState.CONNECTING):
            if self.connecting_scan:
                self.start_connect(self.connecting_scan, self.streaming)

                if self.remote_tab:
                    self.logger.info("Reconnecting to {}...".format(
                        self.remote_tab.serial_number))
                    self.remote_tab.set_disconnected("Reconnecting...")

    def set_ui_state(self, new_state):
        if self.state == RadioPanelState.RUNNING_FUNCTION:
            if self.finish_function:
                self.finish_function()
                self.finish_function = None

        if (new_state == RadioPanelState.STOPPED or
                new_state == RadioPanelState.RUNNING_FUNCTION):
            self.actionBulkClaim.setEnabled(False)
            self.actionBulkUpdateFirmware.setEnabled(False)
            self.actionConnectAnyBootloader.setEnabled(False)
            self.actionConnectNoStreaming.setEnabled(False)
            self.actionConnectSpecificBootloader.setEnabled(False)
            self.actionConnectSpecificSerial.setEnabled(False)
            self.detailScanButton.setEnabled(False)
            self.deviceList.setEnabled(False)
            self.clearButton.setEnabled(False)
            self.disconnectButton.setEnabled(False)
            self.goToRemoteButton.setEnabled(False)

            self.connectButton.setText(self.tr("Connect"))
            self.connectButton.setEnabled(False)

            if new_state == RadioPanelState.RUNNING_FUNCTION:
                self.device_tab.rgb_remote_disconnected()
        elif new_state == RadioPanelState.IDLE:
            self.actionBulkClaim.setEnabled(True)
            self.actionBulkUpdateFirmware.setEnabled(True)
            self.actionConnectAnyBootloader.setEnabled(True)
            self.actionConnectNoStreaming.setEnabled(True)
            self.actionConnectSpecificBootloader.setEnabled(True)
            self.actionConnectSpecificSerial.setEnabled(True)
            self.detailScanButton.setEnabled(True)
            self.deviceList.setEnabled(True)
            self.clearButton.setEnabled(True)
            self.disconnectButton.setEnabled(False)
            self.goToRemoteButton.setEnabled(False)

            self.connectButton.setText(self.tr("Connect"))
            selected = self.get_selected_scan() is not None
            self.connectButton.setEnabled(selected)

            self.device_tab.rgb_remote_disconnected()
        elif new_state == RadioPanelState.CONNECTING:
            self.actionBulkClaim.setEnabled(False)
            self.actionBulkUpdateFirmware.setEnabled(False)
            self.actionConnectAnyBootloader.setEnabled(False)
            self.actionConnectNoStreaming.setEnabled(False)
            self.actionConnectSpecificBootloader.setEnabled(False)
            self.actionConnectSpecificSerial.setEnabled(False)
            self.detailScanButton.setEnabled(False)
            self.deviceList.setEnabled(False)
            self.clearButton.setEnabled(False)
            self.disconnectButton.setEnabled(True)
            self.goToRemoteButton.setEnabled(False)

            self.connectButton.setText(self.tr("Connecting..."))
            self.connectButton.setEnabled(False)

            self.device_tab.rgb_remote_disconnected()
        else:  # new_state == RadioPanelState.CONNECTED:
            self.actionBulkClaim.setEnabled(False)
            self.actionBulkUpdateFirmware.setEnabled(False)
            self.actionConnectAnyBootloader.setEnabled(False)
            self.actionConnectNoStreaming.setEnabled(False)
            self.actionConnectSpecificBootloader.setEnabled(False)
            self.actionConnectSpecificSerial.setEnabled(False)
            self.detailScanButton.setEnabled(False)
            self.deviceList.setEnabled(False)
            self.clearButton.setEnabled(False)
            self.disconnectButton.setEnabled(True)
            self.goToRemoteButton.setEnabled(True)

            self.connectButton.setText(self.tr("Connected"))
            self.connectButton.setEnabled(False)

            self.device_tab.rgb_remote_connected()
        self.state = new_state

    def close_remote_tab(self):
        if self.remote_tab:
            self.logger.info("Closed connection to {}".format(
                self.remote_tab.serial_number))
            self.device_tab.plotmain.close_tab(self.remote_tab)
            self.remote_tab = None

    def start_connect(self, scan, streaming=True):
        self.connecting_scan = scan

        # clear out other entries in the lists
        self.deviceList.clear()
        self.temporary_scan = None
        self.scan_serials.clear()
        self.scans.clear()
        last_seen = self.last_seen.get(scan.serial_number)
        self.last_seen.clear()
        if last_seen:
            self.last_seen[scan.serial_number] = last_seen
        self.device_list_additions.clear()

        self.update_scan_count()

        self.set_selected_scan(scan, temporary=True)

        self.streaming = streaming

        active_scan_database.update_connected(self, scan.serial_number)

        if self.active_scan_serial is not None:
            # we may perform this later as it's in the queue,
            # but we should let go of it while connected
            active_scan_database.active_scan_finished(
                self.active_scan_serial, None)
            self.active_scan_serial = None

        self.set_ui_state(RadioPanelState.CONNECTING)
        if self.tx_control_pipe is not None:
            self.tx_control_pipe.send(("connect", scan.serial_number,
                                       scan.is_bootloader))

    def start_disconnect(self):
        self.set_ui_state(RadioPanelState.IDLE)
        self.close_remote_tab()
        if self.tx_control_pipe is not None:
            self.tx_control_pipe.send(("disconnect",))

        # remove all the old scans
        if self.connecting_scan:
            scan = ScanResult(self.connecting_scan.serial_number,
                              self.connecting_scan.is_bootloader, 0, 0, None)

            self.deviceList.clear()
            self.temporary_scan = None
            self.scan_serials.clear()
            self.scans.clear()
            self.last_seen.clear()
            self.device_list_additions.clear()

            self.update_scan_count()

            self.set_selected_scan(scan, temporary=True)

        self.detail_scan_dialog.clear()

        active_scan_database.update_connected(self, None)

    def connect_button_cb(self):
        scan = self.get_selected_scan()
        if scan:
            self.start_connect(scan)

    def connect_no_streaming_cb(self):
        scan = self.get_selected_scan()
        if scan:
            self.start_connect(scan, streaming=False)

    def connect_any_bootloader_cb(self):
        scan = ScanResult(-1 & 0xFFFFFFFF, True, 0, 0, None)
        self.start_connect(scan)

    def connect_specific_bootloader_cb(self):
        sn, ok = QtWidgets.QInputDialog.getInt(
            None, self.tr("Bootloader Serial"),
            self.tr("Input bootloader serial number"))
        if not ok:
            return
        scan = ScanResult(sn & 0xFFFFFFFF, True, 0, 0, None)
        self.start_connect(scan)

    def connect_specific_serial_cb(self):
        sn, ok = QtWidgets.QInputDialog.getInt(
            None, self.tr("Device Serial"),
            self.tr("Input device serial number"))
        if not ok:
            return
        scan = ScanResult(sn & 0xFFFFFFFF, False, 0, 0, None)
        self.start_connect(scan)

    def disconnect_button_cb(self):
        self.start_disconnect()

    def show_remote_tab(self):
        if self.remote_tab:
            self.device_tab.plotmain.show_tab(
                self.remote_tab, src=self.device_tab)

    def update_list_item(self, list_item, scan):
        text_elements = []

        if scan.serial_number != (-1 & 0xFFFFFFFF):
            text_elements.append(str(scan.serial_number))
        else:
            text_elements.append("Any")

        if scan.serial_number == self.default_serial:
            text_elements.append("<Auto>")

        now = datetime.datetime.now(datetime.timezone.utc)
        last_seen = self.last_seen.get(scan.serial_number)
        if last_seen is not None and (now - last_seen).total_seconds() >= 5:
            # stale
            text_elements.append("(?)")
        elif scan.scan_strength is not None:
            if scan.scan_strength >= -30:
                bars = "\u2581\u200A\u2582\u200A\u2583\u200A\u2585\u200A\u2587"
            elif scan.scan_strength >= -40:
                bars = "\u2581\u200A\u2582\u200A\u2583\u200A\u2585\u200A\u2581"
            elif scan.scan_strength >= -50:
                bars = "\u2581\u200A\u2582\u200A\u2583\u200A\u2581\u200A\u2581"
            elif scan.scan_strength >= -60:
                bars = "\u2581\u200A\u2582\u200A\u2583\u200A\u2581\u200A\u2581"
            else:
                bars = "\u2581\u200A\u2581\u200A\u2581\u200A\u2581\u200A\u2581"
            text_elements.append(f"({bars} {scan.scan_strength} dBm)")

        if scan.is_bootloader:
            text_elements.append("bootloader")

        device_info = active_scan_database.get_scan_info(scan.serial_number)
        if device_info:
            text_elements.append("-")
            text_elements.append(device_info['board_info'][0])

        list_item.setText(" ".join(text_elements))

    def set_selected_scan(self, scan, temporary=False):
        # bring the list up to date
        self.handle_device_list_additions()

        sn = scan.serial_number
        # check if it's already the temporary item
        if self.temporary_scan:
            index = self.scan_serials.index(self.temporary_scan.serial_number)

            if temporary and self.temporary_scan.serial_number == sn:
                # update the temporary scan
                self.temporary_scan = scan
                self.scan_serials[index] = sn
                self.scans[index] = scan
                self.update_list_item(self.deviceList.item(index), scan)
                self.deviceList.setCurrentRow(index)
                return

            # remove the temporary scan
            self.temporary_scan = None
            del self.scan_serials[index]
            del self.scans[index]
            self.deviceList.takeItem(index)

        # see if it's in the main list (there is no temporary at this point)
        index = bisect.bisect_left(self.scan_serials, sn)
        if index != len(self.scan_serials) and self.scan_serials[index] == sn:
            # already in the list
            old_scan = self.scans[index]
            new_scan = ScanResult(sn, scan.is_bootloader, *old_scan[2:])
            self.scans[index] = new_scan
            self.update_list_item(self.deviceList.item(index), new_scan)
            self.deviceList.setCurrentRow(index)
        else:
            # need to create a new entry
            if temporary:
                self.temporary_scan = scan

            list_item = QtWidgets.QListWidgetItem()
            self.update_list_item(list_item, scan)

            self.scan_serials.insert(index, sn)
            self.scans.insert(index, scan)
            self.deviceList.insertItem(index, list_item)
            self.deviceList.setCurrentRow(index)

            self.update_scan_count()

    def get_selected_scan(self):
        self.handle_device_list_additions()

        row = self.deviceList.currentRow()
        if row == -1:
            return None
        else:
            return self.scans[row]

    def handle_scan(self, scan, last_seen):
        sn = scan.serial_number
        self.last_seen[sn] = last_seen

        # pass info to interested parties
        self.detail_scan_dialog.handle_scan(scan, last_seen)
        active_scan_database.regular_scan_ready(scan)

        # start active scan if warranted
        if self.active_scan_serial is None:
            if self.tx_control_pipe is not None:
                if active_scan_database.should_start_active_scan(sn):
                    self.tx_control_pipe.send(
                        ("active scan", sn, scan.is_bootloader))
                    self.active_scan_serial = sn

        if self.temporary_scan and self.temporary_scan.serial_number == sn:
            # it's no longer temporary
            self.temporary_scan = None

        # find the entry if it exists
        index = bisect.bisect_left(self.scan_serials, sn)
        if (index != len(self.scan_serials) and
                self.scan_serials[index] == sn):
            # already in the list
            self.scans[index] = scan
            # don't update now, it'll get updated next time the timer fires
        else:
            # need to create a new entry
            list_item = QtWidgets.QListWidgetItem()
            self.update_list_item(list_item, scan)
            self.scan_serials.insert(index, sn)
            self.scans.insert(index, scan)
            self.device_list_additions.append((index, list_item))

            self.update_scan_count()

    def handle_active_scan(self, serial_number, device_info, last_seen):
        active_scan_database.active_scan_finished(serial_number, device_info)
        self.active_scan_serial = None

    def current_row_changed_cb(self, row=-1):
        if row == -1:
            self.connectButton.setEnabled(False)
        else:
            self.connectButton.setEnabled(True)

    def item_double_clicked_cb(self, item):
        self.handle_device_list_additions()
        if self.state == RadioPanelState.IDLE:
            row = self.deviceList.row(item)
            if row != -1:
                self.start_connect(self.scans[row])

    def start_bulk_claim(self):
        self.set_ui_state(RadioPanelState.RUNNING_FUNCTION)
        self.finish_function = None
        self.tx_control_pipe.send(("function", bulk_claim))

    def start_bulk_update_firmware(self):
        dialog = BulkUpdateFirmwareDialog(self.supports_scan_power,
                                          parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user canceled

        results = dialog.get_results()
        firm_file = results['firmware_location']

        try:
            firm_data = bootloader.decode_firm_file(firm_file)
        except Exception:
            self.logger.exception('Error loading firmware from "%s"',
                                  firm_file)
            m = self.tr('Error loading firmware from file!').format(firm_file)
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), m)
            return

        rx, tx = multiprocessing.Pipe(False)
        self.bulk_update_rx_pipe = rx
        self.bulk_update_tx_pipe = tx
        rx, tx = multiprocessing.Pipe(False)
        self.cancel_rx_pipe = rx
        self.cancel_tx_pipe = tx

        # setup the progress dialog
        self.bulk_update_progress.setMinimum(0)
        self.bulk_update_progress.setMaximum(0)
        self.bulk_update_progress.setValue(0)
        self.bulk_update_progress.setLabelText(self.tr("Initializing..."))
        self.bulk_update_progress.forceShow()

        self.bulk_update_progress_timer.start(20)  # 20 milliseconds

        valid_range = range(results['min_serial'], results['max_serial'] + 1)

        self.set_ui_state(RadioPanelState.RUNNING_FUNCTION)
        self.finish_function = self.bulk_update_finished
        self.tx_control_pipe.send((
            "function", bulk_update, self.bulk_update_tx_pipe,
            self.cancel_rx_pipe, firm_data, valid_range,
            results['device_mode'], results['radio_strength']))

    def bulk_update_canceled(self):
        if self.cancel_tx_pipe is not None:
            self.cancel_tx_pipe.send(True)

    def bulk_update_progress_cb(self):
        last_value = None
        while self.bulk_update_rx_pipe.poll():
            try:
                data = self.bulk_update_rx_pipe.recv()
                if isinstance(data, str):
                    self.bulk_update_progress.setLabelText(data)
                if isinstance(data, tuple):
                    self.bulk_update_progress.setMinimum(data[0])
                    self.bulk_update_progress.setMaximum(data[1])
                if isinstance(data, int):
                    last_value = data
            except EOFError:
                break
        if last_value is not None:
            self.bulk_update_progress.setValue(last_value)

    def bulk_update_finished(self):
        self.bulk_update_progress_timer.stop()
        self.bulk_update_progress.reset()

        # close the pipes
        self.bulk_update_rx_pipe.close()
        self.bulk_update_tx_pipe.close()
        self.cancel_rx_pipe.close()
        self.cancel_tx_pipe.close()
        self.cancel_rx_pipe = None
        self.cancel_tx_pipe = None

    def detail_scan(self):
        # run the dialog
        ret = self.detail_scan_dialog.exec_()

        if ret == 0:
            return  # user canceled

        scan = self.detail_scan_dialog.get_selected_scan()
        if scan:
            self.start_connect(scan)

    def remote_connected(self, device_info):  # called from remote panel
        self.device_tab.rgb_remote_streaming()

        active_scan_database.active_scan_finished(
            self.connecting_scan.serial_number, device_info)

    def update_device_list(self):
        self.handle_device_list_additions()

        if self.state == RadioPanelState.IDLE:
            for index, scan in enumerate(self.scans):
                list_item = self.deviceList.item(index)
                self.update_list_item(list_item, scan)

    def clear_list(self):
        self.deviceList.clear()
        self.temporary_scan = None
        self.scan_serials.clear()
        self.scans.clear()
        self.last_seen.clear()
        self.device_list_additions.clear()

        if self.default_serial:
            scan = ScanResult(self.default_serial, False, 0, 0, None)
            self.set_selected_scan(scan)

        self.update_scan_count()

    def update_scan_count(self):
        text = "Clear ({})".format(len(self.scans))
        self.clearButton.setText(text)
        self.clearButton.setToolTip(text)

    def handle_device_list_additions(self):
        updated = False
        try:
            while True:
                index, list_item = self.device_list_additions.popleft()

                if not updated:
                    updated = True
                    self.deviceList.setUpdatesEnabled(False)

                self.deviceList.insertItem(index, list_item)
        except IndexError:
            pass

        if updated:
            self.deviceList.setUpdatesEnabled(True)
