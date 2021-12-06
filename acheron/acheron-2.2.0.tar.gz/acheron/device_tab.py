import collections
import copy
import datetime
import functools
import io
import json
import logging
import lzma
import math
import multiprocessing
import os
import struct
import time

import numpy
from PySide2 import QtCore, QtGui, QtWidgets
import pyqtgraph

import asphodel
import hyperborea.alert
import hyperborea.calibration
import hyperborea.device_info
from hyperborea.preferences import read_bool_setting, write_bool_setting
from hyperborea.preferences import read_int_setting
import hyperborea.proxy
import hyperborea.stream
import hyperborea.unit_preferences

from .calc_process import CalcProcess
from .calibration import CalibrationPanel
from .change_stream_dialog import ChangeStreamDialog
from .ctrl_var_panel import CtrlVarPanel
from .ctrl_var_widget import CtrlVarWidget
from .edit_alert_dialog import EditAlertDialog
from .info_dialog import InfoDialog
from .hardware_tests import HardwareTestDialog
from .led_control_widget import LEDControlWidget
from .radio_panel import RadioPanel
from .remote_panel import RemotePanel
from .rf_power_panel import RFPowerPanel
from .rf_test_dialog import RFTestDialog
from .rgb_control_widget import RGBControlWidget
from .setting_dialog import SettingDialog
from . import bootloader
from .ui_device_tab import Ui_DeviceTab

logger = logging.getLogger(__name__)


def reset_and_reconnect(device):
    device.reset()
    device.reconnect()


def explode(device):
    raise Exception("Explosion")


def write_nvm(device, new_nvm):
    device.erase_nvm()
    device.write_nvm_section(0, new_nvm)


def reset_rf_power_timeout(device, timeout):
    try:
        device.reset_rf_power_timeout(timeout)
    except asphodel.AsphodelError as e:
        if e.args[1] != "ERROR_CODE_UNIMPLEMENTED_COMMAND":
            raise


def set_device_mode(device, new_mode):
    try:
        device.set_device_mode(new_mode)
        return True, new_mode
    except asphodel.AsphodelError as e:
        if e.args[1] == "ERROR_CODE_INVALID_DATA":
            return False, new_mode
        else:
            raise


def do_rf_test(device, test_type, params):
    try:
        if test_type == "fixed":
            device.do_radio_fixed_test(**params)
        else:  # sweep
            device.do_radio_sweep_test(**params)
        return (True, None)
    except asphodel.AsphodelError as e:
        return False, e


ChannelInformation = collections.namedtuple(
    'ChannelInformation', [
        "name",
        "channel_id",
        "stream_id",
        "subchannel_names",  # list of names
        "unit_str",
        "unit_scale",  # None for non-SI
        "unit_formatter",
        "rate_info",
        "samples",
        "rate",
        "downsample_factor",
        "mean_len",
        "plot_len",
        "fft_shortened",
        "fft_sample_len",
        "fft_freq_axis",
        "fft_size",
    ])


class GUILogHandler(logging.Handler):
    """
    A handler class that exposes a Qt Signal to allow thread-safe logging.
    """

    class InternalQObject(QtCore.QObject):
        loggedMessage = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.internalQObject = self.InternalQObject()
        self.loggedMessage = self.internalQObject.loggedMessage

    def emit(self, record):
        message = self.format(record)
        self.loggedMessage.emit(message)


class SimpleExceptionFormatter(logging.Formatter):
    """
    a logging.Formatter to only show basic exception info (e.g. no stack)
    """
    def format(self, record):
        record = copy.copy(record)
        record.msg = record.msg.rsplit("\n", maxsplit=1)[-1]
        return super().format(record)


class MeasurementLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.alert = False

        self.setReadOnly(True)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.setFixedWidth(100)

        self.copy_action = QtWidgets.QAction(self)
        self.copy_action.setText(self.tr("Copy All"))
        self.copy_action.setShortcut(QtGui.QKeySequence.Copy)
        self.copy_action.setShortcutContext(QtCore.Qt.WidgetShortcut)
        self.copy_action.triggered.connect(self.copy_cb)
        self.addAction(self.copy_action)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    def copy_cb(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.text())

    def set_alert(self, new_alert):
        if new_alert and not self.alert:
            self.alert = True
            self.setStyleSheet("* { color: black; background-color: red; }")
        if self.alert and not new_alert:
            self.alert = False
            self.setStyleSheet("")


class DeviceTab(QtWidgets.QWidget, Ui_DeviceTab):
    name_update = QtCore.Signal(str)
    close_pressed = QtCore.Signal()
    disconnected_signal = QtCore.Signal()
    log_message = QtCore.Signal(int, str, object, object)
    firmware_progress_set_max = QtCore.Signal(int)
    firmware_progress_set_value = QtCore.Signal(int)
    collapsed_set = QtCore.Signal(bool)

    def __init__(self, serial_number, base_dir, diskcache, parent=None,
                 stream_list=True, disable_streaming=False,
                 disable_archiving=False, upload_manager=None,
                 alert_manager=None, collapsed=False):
        super().__init__(parent)

        self.plotmain = parent
        self.stream_list = stream_list  # NOTE: True means activate all streams
        self.disable_streaming = disable_streaming
        self.disable_archiving = disable_archiving

        self.upload_manager = upload_manager
        self.alert_manager = alert_manager

        self.collapsed = collapsed

        self.allow_reconnect = False

        self.settings = QtCore.QSettings()
        self.read_settings()

        self.proxy = None
        self.device_info = None
        self.serial_number = serial_number
        self.base_dir = base_dir
        self.diskcache = diskcache

        self.rgb_widgets = []
        self.led_widgets = []
        self.ctrl_var_widgets = []
        self.panels = []
        self.calibration_panel = None

        self.channel_infos = []  # ChannelInformation
        self.subchannel_fields = {}  # k: channel_index, v: [(mean, std dev),]
        self.channel_indexes = {}  # mapping from channel id to channel index
        self.channel_data = {}  # k: channel_index, v: (mean, std)

        self.streaming = False
        self.calc_process = None

        self.time_curves = []
        self.legend = None

        self.alerts = {}  # k: (ch, subch), v: (mean_l, mean_h, std_l, std_h)
        self.alerts_triggered = {}  # k: (ch, subch), v: [boolean] * 4
        self.alerts_value = {}  # k: (ch, subch), v: [float] * 4

        self.last_channel_index = None  # last plotted channel
        self.last_plot_range_channel_index = None  # last loaded plot range

        self.saved_plot_ranges = {}

        self.lost_packet_count = 0
        self.lost_packet_last_time = None
        self.recent_lost_packet_highlight = False
        self.last_displayed_packet_count = 0
        self.last_displayed_packet_time = None

        self.is_shown = False

        self.setupUi(self)
        self.extra_ui_setup()

        self.setup_logging()
        self.setup_callbacks()
        self.setup_proxy_operations()
        self.setup_graphics()

    def extra_ui_setup(self):
        # make status label visible (this is easily forgotten in QtDesigner)
        self.stackedWidget.setCurrentIndex(0)

        # hide status progress bar
        self.statusProgressBar.setVisible(False)

        # clear out the labels
        self.serialNumber.setText(self.serial_number)
        self.userTag1.setText("")
        self.userTag2.setText("")
        self.boardInfo.setText("")
        self.buildInfo.setText("")
        self.buildDate.setText("")
        self.branch.setText("")
        self.bootloaderIndicator.setVisible(False)
        self.nvmModifiedIndicator.setVisible(False)

        self.menu = QtWidgets.QMenu(self)
        self.firmware_menu = self.menu.addMenu(
            self.tr("Update Firmware"))
        self.firmware_menu.setEnabled(False)
        self.firmware_menu.addAction(self.actionFirmwareLatestStable)
        self.firmware_menu.addAction(self.actionFirmwareFromBranch)
        self.firmware_menu.addAction(self.actionFirmwareFromCommit)
        self.firmware_menu.addAction(self.actionFirmwareFromFile)
        self.advanced_menu = self.menu.addMenu(
            self.tr("Advanced Actions"))
        self.advanced_menu.addAction(self.actionForceRunBootloader)
        self.advanced_menu.addAction(self.actionForceRunApplication)
        self.advanced_menu.addAction(self.actionForceReset)
        self.advanced_menu.addAction(self.actionRaiseException)
        self.advanced_menu.addAction(self.actionRecoverNVM)
        self.menu.addSeparator()
        self.menu.addAction(self.actionCalibrate)
        self.menu.addAction(self.actionShakerCalibrate)
        if self.show_rf_test:
            self.menu.addSeparator()
            self.menu.addAction(self.actionRFTest)
        self.menu.addSeparator()
        self.menu.addAction(self.actionSetDeviceMode)
        self.menu.addAction(self.actionChangeActiveStreams)
        self.menu.addAction(self.actionRunTests)
        self.menuButton.setMenu(self.menu)

        self.firmware_progress = QtWidgets.QProgressDialog("", "", 0, 100)
        self.firmware_progress.setLabelText(self.tr(""))
        self.firmware_progress.setWindowTitle(self.tr("Firmware Update"))
        self.firmware_progress.setCancelButton(None)
        self.firmware_progress.setWindowModality(QtCore.Qt.WindowModal)
        self.firmware_progress.setMinimumDuration(0)
        self.firmware_progress.setAutoReset(False)
        self.firmware_progress.reset()

        self.actionCalibrate.setIcon(QtGui.QIcon.fromTheme("caliper"))
        self.actionChangeActiveStreams.setIcon(QtGui.QIcon.fromTheme(
            "preferences_edit"))
        self.actionEditDeviceSettings.setIcon(QtGui.QIcon.fromTheme("gear"))
        self.actionFirmwareFromBranch.setIcon(QtGui.QIcon.fromTheme(
            "branch_view"))
        self.actionFirmwareFromCommit.setIcon(QtGui.QIcon.fromTheme(
            "symbol_hash"))
        self.actionFirmwareFromFile.setIcon(QtGui.QIcon.fromTheme(
            "document_plain"))
        self.actionFirmwareLatestStable.setIcon(QtGui.QIcon.fromTheme(
            "branch"))
        self.actionForceReset.setIcon(QtGui.QIcon.fromTheme("redo"))
        self.actionForceRunApplication.setIcon(QtGui.QIcon.fromTheme(
            "application"))
        self.actionForceRunBootloader.setIcon(QtGui.QIcon.fromTheme(
            "flash_yellow"))
        self.actionRaiseException.setIcon(QtGui.QIcon.fromTheme("bomb"))
        self.actionRecoverNVM.setIcon(QtGui.QIcon.fromTheme("document_gear"))
        self.actionRunTests.setIcon(QtGui.QIcon.fromTheme("stethoscope"))
        self.actionSetDeviceMode.setIcon(QtGui.QIcon.fromTheme(
            "text_list_numbers"))
        self.actionCopySerialNumber.setIcon(QtGui.QIcon.fromTheme("copy"))
        self.actionSetUserTag1.setIcon(QtGui.QIcon.fromTheme("tag"))
        self.actionSetUserTag2.setIcon(QtGui.QIcon.fromTheme("tag"))
        self.actionShakerCalibrate.setIcon(QtGui.QIcon.fromTheme("shaker"))
        self.actionShowDeviceInfo.setIcon(QtGui.QIcon.fromTheme("information"))
        self.actionFlushLostPackets.setIcon(QtGui.QIcon.fromTheme("replace2"))
        self.actionShowPacketStats.setIcon(QtGui.QIcon.fromTheme(
            "chart_column"))
        self.firmware_menu.setIcon(QtGui.QIcon.fromTheme("cpu_flash"))
        self.advanced_menu.setIcon(QtGui.QIcon.fromTheme("wrench"))

        # set collapse to known state
        self.set_collapsed(self.collapsed)

        self.deviceInfo.setDefaultAction(self.actionShowDeviceInfo)
        self.copySerialNumber.setDefaultAction(self.actionCopySerialNumber)
        self.setUserTag1.setDefaultAction(self.actionSetUserTag1)
        self.setUserTag2.setDefaultAction(self.actionSetUserTag2)
        self.flushLostPackets.setDefaultAction(self.actionFlushLostPackets)
        self.lostPacketDetails.setDefaultAction(self.actionShowPacketStats)
        self.editDeviceSettings.setDefaultAction(self.actionEditDeviceSettings)

    def setup_logging(self):
        level = logging.INFO

        # create a log handler for the GUI and connect it
        self.gui_log_handler = GUILogHandler()
        self.gui_log_handler.loggedMessage.connect(self.handle_log_message)
        self.gui_log_handler.setLevel(level)

        # create a formatter
        formatter = SimpleExceptionFormatter('[%(asctime)s] %(message)s',
                                             datefmt="%Y-%m-%dT%H:%M:%SZ")
        formatter.converter = time.gmtime
        self.gui_log_handler.setFormatter(formatter)

        # attach the handler to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.gui_log_handler)

        # create a filter for this tab's serial number
        def filter_func(record):
            try:
                serial_number = record.serial_number
            except AttributeError:
                return False
            return serial_number == self.serial_number

        # add the filter function to the handler
        self.gui_log_handler.addFilter(filter_func)

        # create a logger that includes the serial number information
        self.logger = hyperborea.proxy.DeviceLoggerAdapter(
            logger, self.serial_number)

        # make sure the root is set to capture the desired level
        if logger.getEffectiveLevel() > level:
            logger.setLevel(level)

    def setup_callbacks(self):
        self.closeButton.clicked.connect(self.close_cb)
        self.log_message.connect(self.log_callback)

        self.graphChannelComboBox.currentIndexChanged.connect(
            self.graph_channel_changed)
        self.fftSubchannelComboBox.currentIndexChanged.connect(
            self.fft_subchannel_changed)

        self.actionCopySerialNumber.triggered.connect(self.copy_serial_number)
        self.actionSetUserTag1.triggered.connect(self.set_user_tag_1)
        self.actionSetUserTag2.triggered.connect(self.set_user_tag_2)
        self.actionFirmwareLatestStable.triggered.connect(
            self.do_bootloader_latest_stable)
        self.actionFirmwareFromBranch.triggered.connect(
            self.do_bootloader_from_branch)
        self.actionFirmwareFromCommit.triggered.connect(
            self.do_bootloader_from_commit)
        self.actionFirmwareFromFile.triggered.connect(
            self.do_bootloader_from_file)
        self.actionForceRunBootloader.triggered.connect(
            self.force_run_bootloader)
        self.actionForceRunApplication.triggered.connect(
            self.force_run_application)
        self.actionForceReset.triggered.connect(self.force_reset)
        self.actionRaiseException.triggered.connect(self.do_explode)
        self.actionRecoverNVM.triggered.connect(self.recover_nvm)
        self.actionFlushLostPackets.triggered.connect(self.flush_lost_packets)
        self.actionShowPacketStats.triggered.connect(self.show_packet_stats)
        self.actionChangeActiveStreams.triggered.connect(
            self.change_active_streams)
        self.actionShowDeviceInfo.triggered.connect(self.show_device_info)
        self.actionCalibrate.triggered.connect(self.calibrate)
        self.actionShakerCalibrate.triggered.connect(self.shaker_calibrate)
        self.actionRFTest.triggered.connect(self.rf_test)
        self.actionEditDeviceSettings.triggered.connect(self.edit_settings)
        self.actionRunTests.triggered.connect(self.run_tests)
        self.actionSetDeviceMode.triggered.connect(self.set_device_mode)

        self.bootloader_progress_timer = QtCore.QTimer(self)
        self.bootloader_progress_timer.timeout.connect(
            self.bootloader_progress_cb)

        self.firmware_progress_set_max.connect(
            self.firmware_progress.setMaximum)
        self.firmware_progress_set_value.connect(
            self.firmware_progress.setValue)

        self.device_info_progress_timer = QtCore.QTimer(self)
        self.device_info_progress_timer.timeout.connect(
            self.device_info_progress_cb)

        self.firmware_finder = hyperborea.download.FirmwareFinder()
        self.firmware_finder.completed.connect(self.firmware_finder_completed)
        self.firmware_finder.error.connect(self.firmware_finder_error)
        self.ref_finder = hyperborea.download.RefFinder()
        self.ref_finder.completed.connect(self.ref_finder_completed)
        self.ref_finder.error.connect(self.ref_finder_error)
        self.downloader = hyperborea.download.Downloader()
        self.downloader.completed.connect(self.download_completed)
        self.downloader.error.connect(self.download_error)

        self.collapseButton.clicked.connect(self.toggle_collapsed)

    def setup_proxy_operations(self):
        self.get_device_info_op = hyperborea.proxy.DeviceOperation(
            hyperborea.device_info.get_device_info)
        self.get_device_info_op.completed.connect(self.device_info_cb)
        self.get_device_info_op.error.connect(self.device_info_error)
        self.set_rgb_op = hyperborea.proxy.SimpleDeviceOperation(
            "set_rgb_values")
        self.set_led_op = hyperborea.proxy.SimpleDeviceOperation(
            "set_led_value")
        self.set_ctrl_var_op = hyperborea.proxy.SimpleDeviceOperation(
            "set_ctrl_var")
        self.set_rf_power_op = hyperborea.proxy.SimpleDeviceOperation(
            "enable_rf_power")
        self.reset_rf_power_timeout_op = hyperborea.proxy.DeviceOperation(
            reset_rf_power_timeout)
        self.start_streaming_op = hyperborea.proxy.DeviceOperation(
            hyperborea.stream.start_streaming)
        self.stop_streaming_op = hyperborea.proxy.DeviceOperation(
            hyperborea.stream.stop_streaming)
        self.stop_streaming_op.completed.connect(self.stop_streaming_cb)
        self.restart_streaming_op = hyperborea.proxy.DeviceOperation(
            hyperborea.stream.stop_streaming)  # restart does the stop
        self.restart_streaming_op.completed.connect(self.restart_streaming_cb)
        self.restart_streaming_op.error.connect(self.restart_streaming_cb)
        self.close_device_op = hyperborea.proxy.SimpleDeviceOperation("close")
        self.write_nvm_op = hyperborea.proxy.DeviceOperation(write_nvm)
        self.write_nvm_op.completed.connect(self.write_nvm_cb)
        self.write_nvm_op.error.connect(self.write_nvm_error)
        self.bootloader_op = hyperborea.proxy.DeviceOperation(
            bootloader.do_bootload)
        self.bootloader_op.completed.connect(self.do_bootloader_cb)
        self.bootloader_op.error.connect(self.bootloader_error)
        self.force_bootloader_op = hyperborea.proxy.DeviceOperation(
            bootloader.force_bootloader)
        self.force_bootloader_op.completed.connect(self.force_reset_cb)
        self.force_bootloader_op.error.connect(self.force_reset_error)
        self.force_application_op = hyperborea.proxy.DeviceOperation(
            bootloader.force_application)
        self.force_application_op.completed.connect(self.force_reset_cb)
        self.force_application_op.error.connect(self.force_reset_error)
        self.force_reset_op = hyperborea.proxy.DeviceOperation(
            reset_and_reconnect)
        self.force_reset_op.completed.connect(self.force_reset_cb)
        self.force_reset_op.error.connect(self.force_reset_error)

        self.set_device_mode_op = hyperborea.proxy.DeviceOperation(
            set_device_mode)
        self.set_device_mode_op.completed.connect(self.set_device_mode_cb)

        self.do_rf_test_op = hyperborea.proxy.DeviceOperation(do_rf_test)
        self.do_rf_test_op.completed.connect(self.do_rf_test_cb)

    def read_settings(self):
        self.auto_rgb = read_bool_setting(self.settings, "AutoRGB", True)
        self.downsample = read_bool_setting(self.settings, "Downsample", True)
        self.plot_mean = read_bool_setting(self.settings, "PlotMean", False)

        self.update_timer_interval = read_int_setting(
            self.settings, "UpdateTimerInterval", 100)
        self.graph_timer_interval = read_int_setting(
            self.settings, "GraphTimerInterval", 100)
        self.stream_timeout = read_int_setting(
            self.settings, "StreamTimeout", 1000)

        self.show_rf_test = read_bool_setting(self.settings, "RFTest", False)

    def handle_log_message(self, message):
        # check if the scroll window is already at the bottom
        scrollBar = self.logList.verticalScrollBar()
        atBottom = scrollBar.value() == scrollBar.maximum()

        # log the message
        logItem = QtWidgets.QListWidgetItem(message)
        self.logList.addItem(logItem)

        # adjust the scroll position if necessary
        if atBottom:
            self.logList.scrollToBottom()

    def update_preferences(self, base_dir, upload_manager, alert_manager):
        self.read_settings()

        self.base_dir = base_dir
        self.upload_manager = upload_manager
        self.alert_manager = alert_manager

        self.restart_streaming()

    def update_disable_streaming(self, disable_streaming):
        self.disable_streaming = disable_streaming

        self.restart_streaming()

    def update_disable_archiving(self, disable_archiving):
        self.disable_archiving = disable_archiving

        self.restart_streaming()

    def start_proxy_operation(self, operation, *args, **kwargs):
        if not self.proxy:
            self.logger.error("called start_proxy_operation with no proxy: %s",
                              (operation, args, kwargs))
            return
        self.proxy.send_job(operation, *args, **kwargs)

    def setup_graphics(self):
        fft_pen = "c"

        self.timePlot = self.graphicsLayout.addPlot(row=0, col=0)
        self.fftPlot = self.graphicsLayout.addPlot(row=0, col=1)

        self.timePlot.showGrid(x=True, y=True)
        self.fftPlot.showGrid(x=True, y=True)

        self.timePlot.setLabel("bottom", "Time (s)")
        self.fftPlot.setLabel("bottom", "Frequency (Hz)")

        self.timePlot.setTitle("Time Domain")
        self.fftPlot.setTitle("Frequency Domain")

        self.bufferingLabel = pyqtgraph.LabelItem("Buffering", size="12pt")
        self.bufferingLabel.setParentItem(self.fftPlot.graphicsItem())
        self.bufferingLabel.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.bufferingLabel.setVisible(False)
        self.buffering = False

        self.noChannelsTimeLabel = pyqtgraph.LabelItem(
            "No Channels", size="12pt")
        self.noChannelsTimeLabel.setParentItem(self.timePlot.graphicsItem())
        self.noChannelsTimeLabel.anchor(
            itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.noChannelsTimeLabel.setVisible(False)
        self.noChannelsFreqLabel = pyqtgraph.LabelItem(
            "No Channels", size="12pt")
        self.noChannelsFreqLabel.setParentItem(self.fftPlot.graphicsItem())
        self.noChannelsFreqLabel.anchor(
            itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.noChannelsFreqLabel.setVisible(False)

        self.fft_curve = self.fftPlot.plot(pen=fft_pen)

        def override_labelString(axis):
            old_method = axis.labelString

            def new_func(self):
                # take off the leading <span>
                s = old_method()
                i = s.find(">")
                prefix = s[:i + 1]
                s = s[i + 1:]
                # take off the trailing </span>
                i = s.rfind("<")
                suffix = s[i:]
                s = s[:i]
                s = s.strip()
                if s.startswith("(") and s.endswith(")"):
                    s = s.strip("()")
                return "".join((prefix, s, suffix))
            new_method = new_func.__get__(axis)
            axis.labelString = new_method
        override_labelString(self.timePlot.getAxis("left"))
        override_labelString(self.fftPlot.getAxis("left"))

    def set_connected(self):
        self.logger.info("Connected")
        self.stackedWidget.setCurrentIndex(1)
        for panel in self.panels:
            panel.connected(self.device_info)
        self.menuButton.setEnabled(True)
        self.statusProgressBar.setVisible(False)
        self.rgb_streaming()

    def set_disconnected(self, message):
        self.statusLabel.setText(message)
        self.stackedWidget.setCurrentIndex(0)
        for panel in self.panels:
            panel.disconnected()
        self.menuButton.setEnabled(False)

    def proxy_disconnect_cb(self):
        self.set_disconnected(self.tr("Disconnected"))
        self.statusProgressBar.setVisible(False)
        self.proxy = None

        self.streaming = False
        if self.calc_process:
            self.calc_process.stop()

        self.disconnected_signal.emit()

    def set_proxy(self, proxy):
        if self.proxy:
            self.proxy.disconnected.disconnect(self.proxy_disconnect_cb)
        self.proxy = proxy
        self.proxy.disconnected.connect(self.proxy_disconnect_cb)
        self.get_device_info()

    def get_device_info(self):
        if not self.allow_reconnect:
            msg = self.tr("Loading Device Information...")
        else:
            msg = self.tr("Reloading Device Information...")
        self.set_disconnected(msg)

        # setup the progress bar
        self.statusProgressBar.setMinimum(0)
        self.statusProgressBar.setMaximum(0)
        self.statusProgressBar.setValue(0)
        self.statusProgressBar.setVisible(True)

        self.device_info_progress_timer.start(20)  # 20 milliseconds

        rx, tx = multiprocessing.Pipe(False)
        self.device_info_rx_pipe = rx
        self.device_info_tx_pipe = tx
        self.start_proxy_operation(
            self.get_device_info_op, self.allow_reconnect, self.diskcache,
            self.device_info_tx_pipe)

    def device_info_progress_cb(self):
        last_value = None
        while self.device_info_rx_pipe.poll():
            try:
                last_value = self.device_info_rx_pipe.recv()
            except EOFError:
                break
        if last_value is not None:
            self.statusProgressBar.setMaximum(last_value[1])
            self.statusProgressBar.setValue(last_value[0])

    def device_info_error(self):
        self.device_info_progress_timer.stop()
        self.device_info_rx_pipe.close()
        self.device_info_tx_pipe.close()

        self.statusProgressBar.setVisible(False)
        QtCore.QCoreApplication.processEvents()
        if self.proxy:
            self.proxy.close_connection()

    def device_info_cb(self, info):
        # stop progress timer and close pipes
        self.device_info_progress_timer.stop()
        self.device_info_rx_pipe.close()
        self.device_info_tx_pipe.close()

        if not info:
            # error while getting initial info
            self.statusProgressBar.setVisible(False)
            QtCore.QCoreApplication.processEvents()
            if self.proxy:
                self.proxy.close_connection()
            return
        else:
            # set bar to 100%
            self.statusProgressBar.setValue(self.statusProgressBar.maximum())
            QtCore.QCoreApplication.processEvents()

        self.device_info = info

        if info['user_tag_1'] is None:
            self.userTag1.setText(self.tr("<INVALID>"))
            self.display_name = self.serial_number
        elif not info['user_tag_1']:
            self.userTag1.setText(self.tr("<EMPTY>"))
            self.display_name = self.serial_number
        else:
            self.userTag1.setText(info['user_tag_1'])
            self.display_name = info['user_tag_1']

        self.name_update.emit(self.display_name)

        if info['user_tag_2'] is None:
            self.userTag2.setText(self.tr("<INVALID>"))
        elif not info['user_tag_2']:
            self.userTag2.setText(self.tr("<EMPTY>"))
        else:
            self.userTag2.setText(info['user_tag_2'])

        self.boardInfo.setText("{} rev {}".format(*info['board_info']))
        self.buildInfo.setText(info['build_info'])
        self.buildDate.setText(info['build_date'])

        if info['repo_branch']:
            self.branch.setText(info['repo_branch'])
            self.branch.setVisible(True)
            self.branchLabel.setVisible(True)
        else:
            self.branch.setText("")
            self.branch.setVisible(False)
            self.branchLabel.setVisible(False)

        battery_results = []
        for i, (_name, supply) in enumerate(info['supplies']):
            if supply.is_battery:
                supply_results = info['supply_results'][i]
                if supply_results is not None:
                    value, result_flags = supply_results
                    scaled_value = value * supply.scale + supply.offset
                    formatted = asphodel.format_value_ascii(
                        supply.unit_type, supply.scale, scaled_value)
                    if result_flags == 0:
                        # ok
                        batt_str = formatted
                    elif result_flags == asphodel.ASPHODEL_SUPPLY_LOW_BATTERY:
                        # low batt
                        batt_str = ('<span style="background-color: yellow; '
                                    f'color: black;">{formatted}</span>')
                    else:
                        # fail
                        batt_str = ('<span style="background-color: red; '
                                    f'color: black;">{formatted}</span>')

                    battery_results.append(batt_str)
        if battery_results:
            self.battery.setText(", ".join(battery_results))
            self.battery.setVisible(True)
            self.batteryLabel.setVisible(True)
        else:
            self.battery.setVisible(False)
            self.batteryLabel.setVisible(False)

        if info['supports_bootloader']:
            self.bootloaderIndicator.setVisible(True)
        else:
            self.bootloaderIndicator.setVisible(False)

        if info['nvm_modified']:
            self.nvmModifiedIndicator.setVisible(True)
        else:
            self.nvmModifiedIndicator.setVisible(False)

        if len(info['settings']) == 0:
            # No settings on the device
            self.actionEditDeviceSettings.setEnabled(False)
            self.actionEditDeviceSettings.setText("No Device Settings")
        else:
            self.actionEditDeviceSettings.setEnabled(True)
            self.actionEditDeviceSettings.setText("Edit Device Settings")

        self.actionForceRunApplication.setEnabled(info['supports_bootloader'])

        can_run_bootloader = info["bootloader_info"] == "Asphodel"
        self.actionForceRunBootloader.setEnabled(can_run_bootloader)

        bootloader_available = (info['supports_bootloader'] or
                                can_run_bootloader)
        self.firmware_menu.setEnabled(bootloader_available)
        self.actionFirmwareLatestStable.setEnabled(bootloader_available)
        self.actionFirmwareFromBranch.setEnabled(bootloader_available)
        self.actionFirmwareFromCommit.setEnabled(bootloader_available)
        self.actionFirmwareFromFile.setEnabled(bootloader_available)

        self.actionSetDeviceMode.setEnabled(info['supports_device_mode'])

        self.actionRFTest.setEnabled(info['supports_radio'] or
                                     info['supports_remote'])

        self.setup_rgb_and_led_widgets(info['rgb_settings'],
                                       info['led_settings'])
        self.rgb_connected()

        self.setup_panels(info)

        # self.set_connected() will be called when streaming has started
        self.set_disconnected(self.tr("Starting streaming..."))
        QtCore.QCoreApplication.processEvents()

        self.flush_lost_packets()
        self.setup_channels()
        self.start_streaming()

        # clear the graphs
        self.fft_curve.clear()
        self.graph_channel_changed()

        self.create_calibration_panel()

        # successfully loaded
        self.allow_reconnect = True

    def setup_rgb_and_led_widgets(self, rgb_settings, led_settings):
        # clear any existing
        self.rgb_widgets.clear()
        self.led_widgets.clear()

        # clear old widgets
        while True:
            item = self.LEDLayout.takeAt(0)
            if not item:
                break
            item.widget().deleteLater()

        # create widgets
        for i, values in enumerate(rgb_settings):
            self.create_rgb_widget(i, values)
        for i, value in enumerate(led_settings):
            self.create_led_widget(i, value)

    def setup_panels(self, info):
        # remove old ones
        for panel in self.panels:
            self.panelLayout.removeWidget(panel)
            panel.deleteLater()
        self.panels.clear()
        self.ctrl_var_widgets.clear()

        # create new ones
        for i, (name, ctrl_var_info, setting) in enumerate(info['ctrl_vars']):
            self.create_ctrl_var_widget(i, name, ctrl_var_info, setting)

        unassigned_ctrl_var_indexes = list(range(len(info['ctrl_vars'])))

        if info['supports_rf_power']:
            self.create_rf_power_panel(info['rf_power_status'])

            for ctrl_var_index in info['rf_power_ctrl_vars']:
                unassigned_ctrl_var_indexes.remove(ctrl_var_index)
                widget = self.ctrl_var_widgets[ctrl_var_index]
                self.rf_power_panel.add_ctrl_var_widget(widget)

        if info['supports_radio']:
            self.create_radio_panel()

            for ctrl_var_index in info['radio_ctrl_vars']:
                unassigned_ctrl_var_indexes.remove(ctrl_var_index)
                widget = self.ctrl_var_widgets[ctrl_var_index]
                self.radio_panel.add_ctrl_var_widget(widget)

        if info['supports_remote']:
            self.create_remote_panel()

        if unassigned_ctrl_var_indexes:
            self.create_ctrl_var_panel(unassigned_ctrl_var_indexes)

    def stop_for_recreate(self):
        self.stop_streaming()

        for panel in self.panels:
            panel.stop()

    def stop_and_close(self):
        self.rgb_disconnected()

        self.stop_streaming()

        for panel in self.panels:
            panel.stop()

        self.start_proxy_operation(self.close_device_op)

        if self.proxy:
            self.proxy.close_connection()

    def close_cb(self):
        self.stop_and_close()
        self.close_pressed.emit()

    def toggle_collapsed(self):
        new_collapsed = not self.collapsed
        # NOTE: don't need to call self.set_collapsed() directly
        self.collapsed_set.emit(new_collapsed)

    def set_collapsed(self, collapsed):
        self.collapsed = collapsed

        if collapsed:
            self.collapseButton.setText(self.tr("\u25B2 Expand \u25B2"))
        else:
            self.collapseButton.setText(self.tr("\u25BC Collapse \u25BC"))
        self.bottomGroup.setVisible(not collapsed)

    def copy_serial_number(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.serial_number)

    def set_user_tag(self, index):
        if not self.device_info:
            # error
            self.logger.exception("No device info available")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                           self.tr("Not yet connected!"))
            return

        # find the current setting
        tag_key = "user_tag_" + str(index + 1)
        old_str = self.device_info[tag_key]

        # ask the user for the new string
        new_str, ok = QtWidgets.QInputDialog.getText(
            self, self.tr("New Tag"), self.tr("New Tag:"),
            QtWidgets.QLineEdit.Normal, old_str)

        if not ok:
            return

        new_str = new_str.strip()

        # find the offset and length
        offset, length = self.device_info['tag_locations'][index]

        self.device_info[tag_key] = new_str
        b = new_str.encode("UTF-8")
        new_nvm = bytearray(self.device_info['nvm'])
        struct.pack_into("{}s".format(length), new_nvm, offset, b)

        # write the new tag
        self.write_nvm(new_nvm)

    def set_user_tag_1(self):
        self.set_user_tag(0)

    def set_user_tag_2(self):
        self.set_user_tag(1)

    def get_firmware_file(self, firm_dir, firm_name):
        settings = QtCore.QSettings()

        board_name, board_rev = self.device_info['board_info']
        short_board_name = board_name.replace(" ", "")

        keys = ["firmDirectory/{}/Rev{}".format(short_board_name, board_rev),
                "firmDirectory/{}/last".format(short_board_name),
                "firmDirectory/last"]

        # find the directory from settings
        firm_dir = None
        for key in keys:
            test_dir = settings.value(key)
            if test_dir and type(test_dir) == str:
                if os.path.isdir(test_dir):
                    firm_dir = test_dir
                    break
        if not firm_dir:
            firm_dir = ""

        # ask the user for the file name
        caption = self.tr("Open Firmware File")
        file_filter = self.tr("Firmware Files (*.firmware);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getOpenFileName(self, caption, firm_dir,
                                                    file_filter)
        output_path = val[0]

        if output_path:
            # save the directory
            output_dir = os.path.dirname(output_path)
            for key in keys:
                settings.setValue(key, output_dir)
            return output_path
        else:
            return None

    def do_bootloader_latest_stable(self):
        self.do_bootloader_web(build_type="firmware", branch="master")

    def do_bootloader_from_branch(self):
        self.firmware_progress.setMinimum(0)
        self.firmware_progress.setMaximum(0)
        self.firmware_progress.setValue(0)
        self.firmware_progress.setLabelText(
            self.tr("Collecting branches..."))
        self.firmware_progress.forceShow()

        self.ref_finder.get_firmware_refs(
            board_info=self.device_info['board_info'])

    def ref_finder_error(self, error_str):
        self.ref_finder_completed([])

    def ref_finder_completed(self, refs):
        self.firmware_progress.reset()

        default_branch = self.device_info.get("repo_branch")
        if not default_branch:
            default_branch = "master"

        branch_choices = [default_branch]
        if default_branch != "master":
            branch_choices.append("master")
        if default_branch != "develop":
            branch_choices.append("develop")

        for ref in refs:
            ref_name = ref.get("name", None)
            if ref_name and ref_name not in branch_choices:
                branch_choices.append(ref_name)

        if refs:
            label = self.tr("Firmware Branch:")
        else:
            label = self.tr("No branches found!\nFirmware Branch:")

        branch, ok = QtWidgets.QInputDialog.getItem(
            self, self.tr("Firmware Branch"), label, branch_choices, 0, True)
        if not ok:
            return

        branch = branch.strip()

        self.do_bootloader_web(build_type=None, branch=branch)

    def do_bootloader_from_commit(self):
        commit, ok = QtWidgets.QInputDialog.getText(
            self, self.tr("Firmware Commit"), self.tr("Firmware Commit:"),
            QtWidgets.QLineEdit.Normal, "")
        if not ok:
            return

        commit = commit.strip()

        self.do_bootloader_web(build_type=None, commit=commit)

    def do_bootloader_web(self, build_type, branch=None, commit=None):
        self.firmware_progress.setMinimum(0)
        self.firmware_progress.setMaximum(0)
        self.firmware_progress.setValue(0)
        self.firmware_progress.setLabelText(
            self.tr("Searching for firmware..."))
        self.firmware_progress.forceShow()

        self.firmware_finder.find_firmware(
            build_type, self.device_info['board_info'], branch=branch,
            commit=commit)

    def firmware_finder_error(self, error_str):
        self.firmware_progress.reset()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)

    def firmware_finder_completed(self, build_urls):
        self.firmware_progress.reset()
        build_types = sorted(build_urls.keys())
        if 'firmware' in build_types:
            # move it to the front
            build_types.remove('firmware')
            build_types.insert(0, 'firmware')

        if len(build_types) == 1:
            # choose the only option available
            build_type = build_types[0]
        else:
            value, ok = QtWidgets.QInputDialog.getItem(
                self, self.tr("Select Build Type"),
                self.tr("Select Build Type"), build_types, 0,
                editable=False)
            if not ok:
                return
            build_type = value

        url = build_urls[build_type]

        self.logger.info("Downloading firmware from %s", url)

        self.firmware_progress.setMinimum(0)
        self.firmware_progress.setMaximum(0)
        self.firmware_progress.setValue(0)
        self.firmware_progress.setLabelText(
            self.tr("Downloading firmware..."))
        self.firmware_progress.forceShow()

        file = io.BytesIO()
        self.downloader.start_download(url, file,
                                       self.download_update_progress)

    def download_update_progress(self, written_bytes, total_length):
        self.firmware_progress_set_max.emit(total_length)
        self.firmware_progress_set_value.emit(written_bytes)

    def download_error(self, file, error_str):
        self.firmware_progress.reset()
        file.close()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)

    def download_completed(self, file):
        self.firmware_progress.reset()
        try:
            firm_data = bootloader.decode_firm_bytes(file.getvalue())
        except Exception:
            self.logger.exception('Error decoding downloaded firmware')
            m = self.tr('Error decoding downloaded firmware!')
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), m)
            return
        finally:
            file.close()
        self.do_bootloader(firm_data)

    def do_bootloader_from_file(self):
        base_dir = self.settings.value("FirmwareRootDir")
        if base_dir:
            base_dir = str(base_dir)  # make sure it's a string
        firm_dir, firm_name = bootloader.get_default_file(self.device_info,
                                                          base_dir)

        if not firm_dir:
            firm_file = self.get_firmware_file(firm_dir, firm_name)
        else:
            firm_file = os.path.join(firm_dir, firm_name)

            message = self.tr("Use {}?").format(firm_file)
            ret = QtWidgets.QMessageBox.question(
                self, self.tr("Update Firmware"), message,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Yes)
            if ret == QtWidgets.QMessageBox.Cancel:
                return False
            if ret == QtWidgets.QMessageBox.No:
                firm_file = self.get_firmware_file(firm_dir, firm_name)

        if not firm_file:
            return  # user cancelled

        try:
            firm_data = bootloader.decode_firm_file(firm_file)
        except Exception:
            self.logger.exception('Error loading firmware from "%s"',
                                  firm_file)
            m = self.tr('Error loading firmware from file!').format(firm_file)
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), m)
            return

        self.do_bootloader(firm_data)

    def do_bootloader(self, firm_data):
        if not bootloader.is_board_supported(firm_data, self.device_info):
            self.logger.error("Firmware file does not support this board!")
            message = self.tr("Firmware file does not support this board!")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)
            return

        if bootloader.already_programmed(firm_data, self.device_info):
            self.logger.info("Firmware already present!")
            message = self.tr("Firmware already present!")
            QtWidgets.QMessageBox.information(self, self.tr("Info"), message)
            return

        self.set_disconnected(self.tr("Stopping Streaming..."))
        self.statusProgressBar.setMinimum(0)
        self.statusProgressBar.setMaximum(0)
        self.statusProgressBar.setValue(0)
        self.statusProgressBar.setVisible(True)

        self.stop_for_recreate()
        rx, tx = multiprocessing.Pipe(False)
        self.bootloader_rx_pipe = rx
        self.bootloader_tx_pipe = tx

        self.allow_reconnect = False

        self.start_proxy_operation(self.bootloader_op, firm_data,
                                   self.bootloader_tx_pipe)

        self.bootloader_progress_timer.start(20)  # 20 milliseconds

    def bootloader_progress_cb(self):
        last_value = None
        while self.bootloader_rx_pipe.poll():
            try:
                data = self.bootloader_rx_pipe.recv()
                if isinstance(data, str):
                    self.statusLabel.setText(data)
                if isinstance(data, tuple):
                    self.statusProgressBar.setMinimum(data[0])
                    self.statusProgressBar.setMaximum(data[1])
                if isinstance(data, int):
                    last_value = data
            except EOFError:
                break
        if last_value is not None:
            self.statusProgressBar.setValue(last_value)

    def do_bootloader_cb(self):
        self.bootloader_progress_timer.stop()
        self.statusProgressBar.setMinimum(0)
        self.statusProgressBar.setMaximum(0)

        # close the pipes
        self.bootloader_rx_pipe.close()
        self.bootloader_tx_pipe.close()

        self.get_device_info()

    def bootloader_error(self):
        self.bootloader_progress_timer.stop()
        self.statusProgressBar.setVisible(False)

        # close the pipes
        self.bootloader_rx_pipe.close()
        self.bootloader_tx_pipe.close()

        self.close_cb()
        message = self.tr("Error while loading firmware!")
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)

    def force_run_bootloader(self):
        self.allow_reconnect = False
        self.set_disconnected(self.tr("Connecting to Bootloader..."))
        self.stop_for_recreate()
        self.start_proxy_operation(self.force_bootloader_op)

    def force_run_application(self):
        self.allow_reconnect = False
        self.set_disconnected(self.tr("Connecting to Application..."))
        self.stop_for_recreate()
        self.start_proxy_operation(self.force_application_op)

    def force_reset(self):
        self.allow_reconnect = False
        self.set_disconnected(self.tr("Resetting Device..."))
        self.stop_for_recreate()
        self.start_proxy_operation(self.force_reset_op)

    def force_reset_cb(self):
        self.get_device_info()

    def force_reset_error(self):
        self.close_cb()
        message = self.tr("Error while reconnecting!")
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)

    def email_callback(self, exception=None):
        if exception is None:
            # ok
            self.log_thread_safe(logging.INFO, "Sent alert email")
        else:
            self.log_thread_safe(logging.ERROR, "Error sending alert email",
                                 exc_info=exception)

    def do_explode(self):
        explode_op = hyperborea.proxy.DeviceOperation(explode)
        self.start_proxy_operation(explode_op)

    def write_nvm(self, nvm):
        nvm = bytes(nvm)
        if self.device_info['nvm'] != nvm:
            self.device_info['nvm'] = nvm
            self.allow_reconnect = False
            self.stop_streaming()
            self.start_proxy_operation(self.write_nvm_op, nvm)
        elif self.device_info['nvm_modified'] is True:
            self.force_reset()
        else:
            self.logger.info("No change to NVM. Skipping write.")
            return

    def recover_nvm(self):
        # ask the user for the file name
        apd_dir = self.base_dir
        caption = self.tr("Open Data File")
        file_filter = self.tr("Data Files (*.apd);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getOpenFileName(self, caption, apd_dir,
                                                    file_filter)
        filename = val[0]
        if filename == "":
            return

        # open file and decompress
        fp = lzma.open(filename, 'rb')

        # read the header from the file
        header_leader = struct.unpack(">dI", fp.read(12))
        header_bytes = fp.read(header_leader[1])
        header_str = header_bytes.decode("UTF-8")
        header = json.loads(header_str)
        new_nvm = bytes.fromhex(header['nvm'])

        # check the nvm lengths
        new_length = len(new_nvm)
        current_length = len(self.device_info['nvm'])
        if new_length != current_length:
            # need to add a popup here #
            message = self.tr("NVM sizes do not match!")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)
            return

        # write the nvm
        self.write_nvm(new_nvm)

    def flush_lost_packets(self):
        if self.calc_process:
            self.calc_process.reset_lost_packets()

        # update UI
        self.recentLostPackets.setText(str(0))
        if self.recent_lost_packet_highlight:
            self.recent_lost_packet_highlight = False
            self.recentLostPackets.setStyleSheet("")

    def show_packet_stats(self):
        count_since_last = (self.lost_packet_count -
                            self.last_displayed_packet_count)
        self.last_displayed_packet_count = self.lost_packet_count

        now = datetime.datetime.utcnow()

        if self.last_displayed_packet_time is not None:
            last_check_str = self.last_displayed_packet_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ")  # use ISO 8601 representation
        else:
            last_check_str = self.tr("Never")
        self.last_displayed_packet_time = now

        if self.lost_packet_last_time is not None:
            delta = now - self.lost_packet_last_time

            # remove microseconds
            delta = delta - datetime.timedelta(microseconds=delta.microseconds)
            last_loss_str = str(delta)
        else:
            last_loss_str = self.tr("N/A")

        msg = ("All Time Lost Packets: {}\nTime since last packet loss: {}\n"
               "Lost Since Last Check: {}\nTime of last check: {}".format(
                   self.lost_packet_count, last_loss_str, count_since_last,
                   last_check_str))

        QtWidgets.QMessageBox.information(self, self.tr("Packet Loss Stats"),
                                          msg)

    def change_active_streams(self):
        dialog = ChangeStreamDialog(self.device_info['streams'],
                                    self.device_info['channels'],
                                    self.stream_list, parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        self.stream_list = dialog.get_new_stream_list()
        self.restart_streaming()

    def show_device_info(self):
        dialog = InfoDialog(self.device_info, parent=self)
        dialog.exec_()

    def run_tests(self):
        self.stop_streaming()
        self.set_disconnected(self.tr("Running Hardware Tests..."))
        dialog = HardwareTestDialog(self.device_info, self.proxy, parent=self)
        dialog.start_tests()
        dialog.exec_()
        self.get_device_info()

    def set_device_mode(self):
        new_mode, ok = QtWidgets.QInputDialog.getInt(
            self, self.tr("Device Mode"), self.tr("Input new device mode"),
            self.device_info['device_mode'], 0, 255)
        if not ok:
            return
        self.start_proxy_operation(self.set_device_mode_op, new_mode)

    def set_device_mode_cb(self, ret):
        success, new_mode = ret
        if success:
            self.device_info['device_mode'] = new_mode
        else:
            self.logger.warning("Bad device mode {}".format(new_mode))
            QtWidgets.QMessageBox.critical(
                self, self.tr("Bad Device Mode"),
                self.tr("Bad Device Mode {}!").format(new_mode))

    def calibrate(self, _junk=None):
        if self.actionCalibrate.isChecked():
            # start
            self.actionCalibrate.setText(self.tr("Stop Calibration"))
            self.calibration_panel.setVisible(True)
        else:
            # stop
            self.actionCalibrate.setText(self.tr("Start Calibration"))
            self.calibration_panel.setVisible(False)

    def shaker_calibrate(self, _junk=None):
        ret = QtWidgets.QMessageBox.information(
            self, self.tr("Calibration"),
            self.tr("Let the shaker run for at least 1 second."),
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        if ret != QtWidgets.QMessageBox.Ok:
            return

        settings = self.device_info['settings']
        unit_type = asphodel.UNIT_TYPE_M_PER_S2
        cal = self.shaker_calibration_info

        index = self.channel_indexes[self.shaker_id]
        mean, std_dev = self.capture_func(index)

        try:
            unscaled_mag = std_dev / cal.scale
            unscaled_offset = (mean - cal.offset) / cal.scale

            scale = 9.80665 / unscaled_mag

            if scale == 0:
                raise Exception("Invalid scale")

            offset = -unscaled_offset * scale
        except Exception:
            msg = "Error performing calibration"
            self.logger.exception(msg)
            QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                           self.tr(msg))
            return

        u, f = hyperborea.calibration.get_channel_setting_values(
            settings, cal, unit_type, scale, offset)
        new_nvm = hyperborea.calibration.update_nvm(
            self.device_info['nvm'], settings, u, f, self.logger)

        self.write_nvm(new_nvm)

    def rf_test(self):
        dialog = RFTestDialog(parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        test_type, params = dialog.get_results()

        self.stop_for_recreate()

        self.start_proxy_operation(self.do_rf_test_op, test_type, params)

    def do_rf_test_cb(self, result):
        success, e = result
        if success:
            message = self.tr("Running RF Test")
        else:
            message = self.tr("Running RF Test\nResponse: {}").format(e)
        self.set_disconnected(message)

    def edit_settings(self):
        settings = self.device_info['settings']
        nvm_bytes = self.device_info['nvm']
        custom_enums = self.device_info['custom_enums']
        setting_categories = self.device_info['setting_categories']
        dialog = SettingDialog(settings, nvm_bytes, custom_enums,
                               setting_categories, parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        try:
            new_nvm = bytearray(nvm_bytes)
            dialog.update_nvm(new_nvm)
        except Exception:
            self.logger.exception("Unhandled Exception in edit_settings")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                           self.tr("Error parsing settings!"))
            return

        self.write_nvm(new_nvm)

    def write_nvm_cb(self):
        self.force_reset()

    def write_nvm_error(self):
        self.close_cb()
        message = self.tr("Error while writing NVM!")
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)

    def create_rgb_widget(self, index, initial_values):
        def set_values(values):
            self.start_proxy_operation(self.set_rgb_op, index, values)

        widget = RGBControlWidget(set_values, initial_values, parent=self)
        self.LEDLayout.addWidget(widget)
        self.rgb_widgets.append(widget)

    def create_led_widget(self, index, initial_value):
        def set_value(value):
            self.start_proxy_operation(self.set_led_op, index, value)

        widget = LEDControlWidget(set_value, initial_value, parent=self)
        self.LEDLayout.addWidget(widget)
        self.led_widgets.append(widget)

    def create_ctrl_var_widget(self, index, name, ctrl_var_info, setting):
        def set_value(value):
            self.start_proxy_operation(self.set_ctrl_var_op, index, value)

        widget = CtrlVarWidget(set_value, name, ctrl_var_info, setting,
                               parent=self)
        self.ctrl_var_widgets.append(widget)

    def create_ctrl_var_panel(self, indexes):
        self.ctrl_var_panel = CtrlVarPanel(parent=self)
        for i in indexes:
            self.ctrl_var_panel.add_ctrl_var_widget(self.ctrl_var_widgets[i])
        self.add_panel(self.ctrl_var_panel)

    def create_rf_power_panel(self, status):
        def enable_func(enable):
            self.start_proxy_operation(self.set_rf_power_op, enable)

        def reset_timeout_func(timeout):
            self.start_proxy_operation(self.reset_rf_power_timeout_op, timeout)

        self.rf_power_panel = RFPowerPanel(enable_func, reset_timeout_func,
                                           status, parent=self)
        self.add_panel(self.rf_power_panel)
        self.plotmain.register_rf_power_panel(self.rf_power_panel)

    def create_radio_panel(self):
        self.radio_panel = RadioPanel(self.start_proxy_operation,
                                      self.diskcache, parent=self)
        self.add_panel(self.radio_panel)

    def create_remote_panel(self):
        self.remote_panel = RemotePanel(parent=self)
        self.add_panel(self.remote_panel)

    def add_panel(self, panel):
        self.panels.append(panel)
        self.panelLayout.addWidget(panel)

    def capture_func(self, channel_index):
        try:
            return self.channel_data[channel_index]
        except KeyError:
            return (math.nan, math.nan)

    def create_calibration_panel(self):
        if self.calibration_panel:
            self.panelLayout.removeWidget(self.calibration_panel)
            self.calibration_panel.deleteLater()

        channel_calibration = self.device_info['channel_calibration']
        cals = []
        for channel_id, calibration_info in enumerate(channel_calibration):
            if calibration_info is not None:
                if channel_id in self.channel_indexes:
                    # setup variables to be used by the shaker calibration
                    # (only available if there is exactly one channel)
                    self.shaker_id = channel_id
                    self.shaker_calibration_info = calibration_info

                    index = self.channel_indexes[channel_id]
                    channel_info = self.channel_infos[index]
                    name = channel_info.name
                    capture = functools.partial(self.capture_func, index)
                    cals.append((name, calibration_info, capture,
                                 channel_info.unit_formatter))
        self.calibration_panel = CalibrationPanel(
            self.device_info, cals, self.logger, parent=self)
        self.calibration_panel.setVisible(False)

        self.actionCalibrate.setEnabled(len(cals) > 0)
        self.actionShakerCalibrate.setEnabled(len(cals) == 1)

        # NOTE: don't add to self.panels, as it doesn't support the panel funcs

        self.panelLayout.insertWidget(0, self.calibration_panel)

    def log_thread_safe(self, level, message, *args, **kwargs):
        self.log_message.emit(level, message, args, kwargs)

    def log_callback(self, level, message, args, kwargs):
        self.logger.log(level, message, *args, **kwargs)

    def unknown_id_cb(self, unknown_id):
        msg = "Unknown ID {} while decoding packet".format(unknown_id)
        self.logger.error(msg)

    def setup_channels(self):
        # clear any old channel information
        self.channel_infos.clear()
        self.channel_indexes.clear()

        # reset the channel layout
        to_delete = []
        for i in range(self.channelLayout.count()):
            row, _col, _rs, _cs = self.channelLayout.getItemPosition(i)
            if row != 0:
                to_delete.append(self.channelLayout.itemAt(i).widget())
        for widget in to_delete:
            self.channelLayout.removeWidget(widget)
            widget.deleteLater()

        streams = self.device_info['streams']
        channels = self.device_info['channels']

        if self.disable_streaming:
            streams_to_activate = []
        elif self.stream_list is True:
            streams_to_activate = list(range(len(streams)))
        else:
            streams_to_activate = self.stream_list

        info_list = []
        for i, stream in enumerate(streams):
            if i not in streams_to_activate:
                continue
            channel_info_list = []
            indexes = stream.channel_index_list[0:stream.channel_count]
            for ch_index in indexes:
                channel_info_list.append(channels[ch_index])
            info_list.append((i, stream, channel_info_list))

        self.device_decoder = asphodel.nativelib.create_device_decoder(
            info_list, self.device_info['stream_filler_bits'],
            self.device_info['stream_id_bits'])

        # key: channel_id, value: (stream_id, channel, decoder)
        channel_decoders = {}

        # set unknown_id and lost packet callbacks, and fill channel_decoders
        for i, stream_decoder in enumerate(self.device_decoder.decoders):
            stream_id = self.device_decoder.stream_ids[i]
            for j, channel_decoder in enumerate(stream_decoder.decoders):
                channel_id = stream_decoder.stream_info.channel_index_list[j]
                channel = channels[channel_id]
                channel_decoders[channel_id] = (stream_id, channel,
                                                channel_decoder)

        # operate on the channel decoders sorted by channel index
        for channel_id in sorted(channel_decoders.keys()):
            stream_id, channel, channel_decoder = channel_decoders[channel_id]
            self.setup_channel(stream_id, streams[stream_id], channel_id,
                               channel, channel_decoder)

        # fill the combo box
        self.graphChannelComboBox.clear()
        for channel_info in self.channel_infos:
            self.graphChannelComboBox.addItem(channel_info.name)
        if self.graphChannelComboBox.count() > 0:
            self.graphChannelComboBox.setCurrentIndex(0)

    def setup_channel(self, stream_id, stream, channel_id, channel,
                      channel_decoder):
        unit_formatter = hyperborea.unit_preferences.create_unit_formatter(
            self.settings, channel.unit_type, channel.minimum, channel.maximum,
            channel.resolution)

        # figure out if the unit formatter follows SI rules
        unit_scale = None
        unit_str = unit_formatter.unit_html
        if unit_formatter.conversion_offset == 0.0:
            uf_1000x = hyperborea.unit_preferences.create_unit_formatter(
                self.settings, channel.unit_type, channel.minimum * 1000.0,
                channel.maximum * 1000.0, channel.resolution)
            ratio = unit_formatter.conversion_scale / uf_1000x.conversion_scale
            if numpy.isclose(1000.0, ratio):
                # it's probably a SI unit formatter
                unit_scale = 1.0 / unit_formatter.conversion_scale

                # find the base string
                uf_base = hyperborea.unit_preferences.create_unit_formatter(
                    self.settings, channel.unit_type, 1.0, 1.0, 1.0)
                unit_str = uf_base.unit_html

        index = len(self.channel_infos)
        self.channel_indexes[channel_id] = index

        subchannel_fields = []

        for i in range(channel_decoder.subchannels):
            subchannel_name = channel_decoder.subchannel_names[i]
            label = QtWidgets.QLabel(subchannel_name)

            mean_field = MeasurementLineEdit()
            std_dev_field = MeasurementLineEdit()
            sampling_rate_field = MeasurementLineEdit()

            sampling_rate_field.setFixedWidth(75)

            sampling_rate = channel.samples * stream.rate
            sampling_rate_field.setText("{:g} sps".format(sampling_rate))

            edit_alert_action = self.create_edit_alert_action(
                channel_id, index, i, subchannel_name, channel.unit_type,
                unit_formatter, mean_field, std_dev_field)
            edit_alert_button = QtWidgets.QToolButton(self)
            edit_alert_button.setDefaultAction(edit_alert_action)

            row = self.channelLayout.rowCount()
            self.channelLayout.addWidget(label, row, 0)
            self.channelLayout.addWidget(mean_field, row, 1)
            self.channelLayout.addWidget(std_dev_field, row, 2)
            self.channelLayout.addWidget(sampling_rate_field, row, 3)
            self.channelLayout.addWidget(edit_alert_button, row, 4)
            subchannel_fields.append((mean_field, std_dev_field))

        rate_info = self.device_info['stream_rate_info'][stream_id]
        channel_rate = channel.samples * stream.rate

        # figure out how much data to collect
        sample_len = math.ceil(10.0 * channel_rate)  # 10 seconds
        # round up to next power of 2 (for faster FFT)
        sample_len = 2 ** (math.ceil(math.log2(sample_len)))

        if self.downsample and sample_len > 32768:
            downsample_factor = channel.samples
        else:
            downsample_factor = 1

        fft_sample_len = min(sample_len, 32768)

        channel_info = ChannelInformation(
            name=channel_decoder.channel_name,
            channel_id=channel_id,
            stream_id=stream_id,
            subchannel_names=channel_decoder.subchannel_names,
            unit_str=unit_str,
            unit_scale=unit_scale,
            unit_formatter=unit_formatter,
            rate_info=rate_info,
            samples=channel.samples,
            rate=channel_rate,
            downsample_factor=downsample_factor,
            mean_len=math.ceil(1.0 * channel_rate),  # 1 second
            plot_len=sample_len // downsample_factor,
            fft_shortened=(fft_sample_len != sample_len),
            fft_sample_len=fft_sample_len,
            fft_freq_axis=numpy.fft.rfftfreq(fft_sample_len, 1 / channel_rate),
            fft_size=fft_sample_len,
        )
        self.channel_infos.append(channel_info)
        self.subchannel_fields[index] = subchannel_fields

    def handle_alerts(self):
        alert_names = ['mean low', 'mean high', 'std low', 'std high']
        active_alerts = []
        for key in sorted(self.alerts.keys()):
            alert_triggered = self.alerts_triggered[key]
            alert_value = self.alerts_value[key]
            for i, (t, v) in enumerate(zip(alert_triggered, alert_value)):
                if t:
                    channel_info = self.channel_infos[key[0]]
                    subchannel_name = channel_info.subchannel_names[key[1]]
                    uf = channel_info.unit_formatter
                    limit = uf.format_ascii(self.alerts[key][i])
                    value = uf.format_ascii(v)
                    a = (subchannel_name, alert_names[i], limit, value)
                    active_alerts.append(a)
        for subchannel_name, alert_name, limit, value in active_alerts:
            s = "{} alert triggered on {}: value {} is outside limit of {}"
            self.logger.warning(s.format(alert_name.capitalize(),
                                         subchannel_name, value, limit))

        if self.alert_manager is not None:
            alerts = []
            for subchannel_name, alert_name, limit, value in active_alerts:
                alerts.append(hyperborea.alert.Alert(subchannel_name,
                                                     alert_name, limit, value))
            self.alert_manager.send_alerts(
                self.serial_number, self.display_name, alerts,
                self.email_callback)

    def create_edit_alert_action(self, channel_id, channel_index,
                                 subchannel_index, subchannel_name, unit_type,
                                 unit_formatter, mean_lineedit, std_lineedit):
        action = QtWidgets.QAction(self)
        action.setText(self.tr("Edit Alert for {}").format(subchannel_name))

        prefix = "{}/AlertCh{}_{}/".format(self.serial_number, channel_id,
                                           subchannel_index)
        alert_keys = ['MeanLow', 'MeanHigh', 'StdLow', 'StdHigh']

        def read_alert_settings():
            alert_enabled = []
            alert_values = []
            for i, key in enumerate(alert_keys):
                enabled = read_bool_setting(
                    self.settings, prefix + key + "Enabled", False)
                try:
                    s = self.settings.value(prefix + key + 'Value')
                    if s is not None:
                        f = float(s)
                        if i < 2:
                            # do scale and offset (mean)
                            v = ((f * unit_formatter.conversion_scale) +
                                 unit_formatter.conversion_offset)
                        else:
                            # do scale (std dev)
                            v = f * unit_formatter.conversion_scale
                        alert_values.append(v)
                    else:
                        alert_values.append(0.0)
                        enabled = False
                except ValueError:
                    alert_values.append(0.0)
                    enabled = False
                alert_enabled.append(enabled)

            return alert_enabled, alert_values

        def update_alert():
            dict_key = (channel_index, subchannel_index)
            alert_enabled, alert_values = read_alert_settings()
            if all(a is False for a in alert_enabled):
                action.setIcon(QtGui.QIcon.fromTheme("signal_flag_white"))
                # remove the alert (if it exists)
                self.alerts.pop(dict_key, None)
            else:
                unit = read_int_setting(self.settings, prefix + "UnitType",
                                        None)
                if unit != unit_type:
                    action.setIcon(QtGui.QIcon.fromTheme("sign_warning"))

                    # log a warning
                    msg = "Alert definition for {} is incorrect!".format(
                        subchannel_name)
                    self.logger.warning(msg)

                    # remove the alert (if it exists)
                    self.alerts.pop(dict_key, None)
                else:
                    action.setIcon(QtGui.QIcon.fromTheme("signal_flag_red"))
                    alert = []
                    for e, v in zip(alert_enabled, alert_values):
                        if e:
                            alert.append(v)
                        else:
                            alert.append(None)
                    self.alerts[dict_key] = alert

            # reset alert state
            try:
                mean_lineedit.set_alert(False)
                std_lineedit.set_alert(False)
            except IndexError:
                pass  # the lineedits don't exist yet

            self.alerts_triggered[dict_key] = [False, False, False, False]
            self.alerts_value[dict_key] = [None, None, None, None]

        def edit_alert():
            alert_enabled, alert_values = read_alert_settings()

            dialog = EditAlertDialog(
                alert_enabled, alert_values, subchannel_name, unit_formatter,
                parent=self)
            ret = dialog.exec_()
            if ret == 0:
                return  # user cancelled

            alert_enabled, alert_values = dialog.get_alert_settings()

            # write the new alert values
            for i, (e, v, key) in enumerate(zip(alert_enabled, alert_values,
                                                alert_keys)):
                write_bool_setting(self.settings, prefix + key + "Enabled", e)
                if i < 2:
                    # do scale and offset (mean)
                    f = ((v - unit_formatter.conversion_offset) /
                         unit_formatter.conversion_scale)
                else:
                    # do scale (std dev)
                    f = v / unit_formatter.conversion_scale
                self.settings.setValue(prefix + key + 'Value', f)

            if all(a is False for a in alert_enabled):
                self.settings.remove(prefix + "UnitType")
            else:
                self.settings.setValue(prefix + "UnitType", unit_type)
            update_alert()

        action.triggered.connect(edit_alert)
        update_alert()

        return action

    def status_callback(self, status):
        if (status.startswith("error")):
            status = status[5:].strip()
            self.logger.error("Error during streaming: {}".format(status))
            self.stop_and_close()
            self.set_disconnected(self.tr("Error"))
        elif (status == "connected"):
            self.set_connected()
        else:
            self.logger.info("Status: {}".format(status))

    def channel_update_cb(self, channel_index, mean, std_dev):
        alert_just_triggered = False

        channel_info = self.channel_infos[channel_index]
        self.channel_data[channel_index] = (mean, std_dev)

        for i, fields in enumerate(self.subchannel_fields[channel_index]):
            # update the text boxes
            mean_field, std_dev_field = fields
            s = channel_info.unit_formatter.format_utf8(mean[i])
            mean_field.setText(s)
            s = channel_info.unit_formatter.format_utf8(std_dev[i])
            std_dev_field.setText(s)

            # check alert
            alert_key = (channel_index, i)
            alert = self.alerts.get(alert_key, None)

            if alert:
                alert_triggered = self.alerts_triggered[alert_key]
                alert_value = self.alerts_value[alert_key]

                # alert is (mean low, mean high, std low, std high)

                if alert[0] is not None and mean[i] <= alert[0]:
                    alert_value[0] = mean[i]
                    if not alert_triggered[0]:
                        alert_triggered[0] = True
                        alert_just_triggered = True
                        mean_field.set_alert(True)
                elif alert_triggered[0]:
                    alert_triggered[0] = False
                    mean_field.set_alert(False)

                if alert[1] is not None and mean[i] >= alert[1]:
                    alert_value[1] = mean[i]
                    if not alert_triggered[1]:
                        alert_triggered[1] = True
                        alert_just_triggered = True
                        mean_field.set_alert(True)
                elif alert_triggered[1]:
                    alert_triggered[1] = False
                    mean_field.set_alert(False)

                if alert[2] is not None and std_dev[i] <= alert[2]:
                    alert_value[2] = std_dev[i]
                    if not alert_triggered[2]:
                        alert_triggered[2] = True
                        alert_just_triggered = True
                        std_dev_field.set_alert(True)
                elif alert_triggered[2]:
                    alert_triggered[2] = False
                    std_dev_field.set_alert(False)

                if alert[3] is not None and std_dev[i] >= alert[3]:
                    alert_value[3] = std_dev[i]
                    if not alert_triggered[3]:
                        alert_triggered[3] = True
                        alert_just_triggered = True
                        std_dev_field.set_alert(True)
                elif alert_triggered[3]:
                    alert_triggered[3] = False
                    std_dev_field.set_alert(False)

        if alert_just_triggered:
            self.handle_alerts()

    def plot_update_cb(self, channel_index, time, data):
        selected_channel_index = self.graphChannelComboBox.currentIndex()
        if channel_index != selected_channel_index:
            # old data
            return

        channel_info = self.channel_infos[channel_index]

        if self.last_channel_index != channel_index:
            self.last_channel_index = channel_index
            if channel_info.downsample_factor == 1:
                self.timePlot.setTitle("Time Domain")
            else:
                s = "Time Domain (Downsampled {}x)".format(
                    channel_info.downsample_factor)
                self.timePlot.setTitle(s)

        for array, curve in zip(data.transpose(), self.time_curves):
            curve.setData(time, array.flatten())

    def fft_update_cb(self, channel_index, subchannel_id, fft_freqs, fft_data):
        selected_channel_index = self.graphChannelComboBox.currentIndex()
        if channel_index != selected_channel_index:
            # old data
            return

        selected_subchannel_index = self.fftSubchannelComboBox.currentIndex()
        if subchannel_id != selected_subchannel_index:
            # old data
            return

        if numpy.ndim(fft_data) == 0:
            # buffering
            if not self.buffering:
                self.bufferingLabel.setVisible(True)
                self.buffering = True

            try:
                percent = int(100 * fft_data)
                text = "Buffering {}%".format(percent)
            except Exception:
                text = "Buffering"
            self.bufferingLabel.setText(text)
        else:
            if self.buffering:
                self.bufferingLabel.setVisible(False)
                self.buffering = False
            self.fft_curve.setData(fft_freqs, fft_data)

    def lost_packet_update(self, total, last_datetime, recent):
        self.lost_packet_count = total
        self.lost_packet_last_time = last_datetime

        self.recentLostPackets.setText(str(recent))
        if recent > 0:
            if not self.recent_lost_packet_highlight:
                self.recent_lost_packet_highlight = True
                self.recentLostPackets.setStyleSheet(
                    "* { color: black; background-color: red }")
        else:
            if self.recent_lost_packet_highlight:
                self.recent_lost_packet_highlight = False
                self.recentLostPackets.setStyleSheet("")

    def create_calc_process(self):
        if self.calc_process:
            self.calc_process.stop()
            self.calc_process.join()

        channel_interval = self.update_timer_interval / 1000
        plot_interval = self.graph_timer_interval / 1000
        fft_interval = self.graph_timer_interval / 1000

        self.calc_process = CalcProcess(
            self.serial_number, self.is_shown, self.device_decoder,
            self.channel_infos, self.channel_indexes, channel_interval,
            plot_interval, fft_interval)

        self.calc_process.status_received.connect(self.status_callback)
        self.calc_process.channel_update.connect(self.channel_update_cb)
        self.calc_process.plot_update.connect(self.plot_update_cb)
        self.calc_process.fft_update.connect(self.fft_update_cb)
        self.calc_process.lost_packet_update.connect(self.lost_packet_update)
        self.calc_process.unknown_id.connect(self.unknown_id_cb)

        # send the current channel and subchannel information
        self.fft_subchannel_changed()

    def start_streaming(self):
        if self.streaming:
            raise AssertionError("Already Streaming")

        compression_level = self.settings.value("CompressionLevel")
        if compression_level is not None:
            try:
                compression_level = int(compression_level)
            except ValueError:
                compression_level = None  # default

        streams = self.device_info['streams']

        if self.disable_streaming:
            indexes = []
        elif self.stream_list is True:
            indexes = list(range(len(streams)))
        else:
            indexes = [i for i in self.stream_list if i < len(streams)]

        active_streams = [s for i, s in enumerate(streams) if i in indexes]

        warm_up_time = 0.0
        for stream in active_streams:
            if stream.warm_up_delay > warm_up_time:
                warm_up_time = stream.warm_up_delay

        if len(active_streams) == 0:
            # No streams: can't start streaming
            if self.buffering:
                self.bufferingLabel.setVisible(False)
                self.buffering = False
            self.noChannelsTimeLabel.setVisible(True)
            self.noChannelsFreqLabel.setVisible(True)

            # use a fallback value for stream_counts
            stream_counts = (1, 1, self.stream_timeout)
        else:
            self.noChannelsTimeLabel.setVisible(False)
            self.noChannelsFreqLabel.setVisible(False)

            stream_counts = asphodel.nativelib.get_streaming_counts(
                active_streams, response_time=0.05, buffer_time=0.5,
                timeout=self.stream_timeout)

        header_dict = self.device_info.copy()
        header_dict['stream_counts'] = stream_counts
        header_dict['streams_to_activate'] = indexes
        header_dict['warm_up_time'] = warm_up_time

        self.streaming = True

        self.create_calc_process()
        packet_pipe, status_pipe = self.calc_process.get_pipes()

        if self.upload_manager is not None:
            rx, tx = multiprocessing.Pipe(False)
            self.upload_rx_pipe = rx
            self.upload_tx_pipe = tx
            self.upload_manager.register_upload_pipe(self.upload_rx_pipe)
        else:
            self.upload_tx_pipe = None

        self.start_proxy_operation(
            self.start_streaming_op, indexes, warm_up_time, stream_counts,
            header_dict, packet_pipe, status_pipe,
            self.display_name, self.base_dir, self.disable_archiving,
            compression_level, self.upload_tx_pipe)

    def stop_streaming(self):
        if self.streaming:
            self.streaming = False
            if self.calc_process:
                self.calc_process.stop()
            self.start_proxy_operation(self.stop_streaming_op)

    def stop_streaming_cb(self):
        if self.calc_process:
            self.calc_process.join()
            self.calc_process = None

    def restart_streaming(self):
        if not self.proxy:
            return

        # partial set_disconnected()
        self.statusLabel.setText(self.tr("Reconnecting"))
        self.stackedWidget.setCurrentIndex(0)
        self.menuButton.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

        if self.streaming:
            self.streaming = False
            self.start_proxy_operation(self.restart_streaming_op)
        else:
            self.do_restart_streaming()

    def do_restart_streaming(self):
        # force restart streaming
        self.last_channel_index = None
        self.setup_channels()
        self.start_streaming()
        self.fft_curve.clear()
        self.graph_channel_changed()

    def restart_streaming_cb(self):
        self.stop_streaming_cb()
        self.do_restart_streaming()

    def get_plot_pens(self, subchannel_count):
        if subchannel_count == 1:
            return ['c']

        pens = ['b', 'g', 'r']
        if subchannel_count <= 3:
            return pens[:subchannel_count]

        return pens + ['c'] * (subchannel_count - len(pens))

    def graph_channel_changed(self, _junk=None):
        self.fftSubchannelComboBox.clear()
        self.timePlot.clear()
        self.time_curves.clear()
        self.fft_curve.clear()

        index = self.graphChannelComboBox.currentIndex()
        if index == -1:
            return

        if self.last_plot_range_channel_index is not None:
            self.save_plot_range(self.last_plot_range_channel_index)

        channel_info = self.channel_infos[index]

        for subchannel_name in channel_info.subchannel_names:
            self.fftSubchannelComboBox.addItem(subchannel_name)

        subchannel_count = len(channel_info.subchannel_names)
        if subchannel_count > 1:
            self.fftSubchannelComboBox.setEnabled(True)
        else:
            self.fftSubchannelComboBox.setEnabled(False)

        # remove the legend
        if self.legend:
            self.legend.scene().removeItem(self.legend)
            self.timePlot.legend = None
            self.legend = None

        if subchannel_count > 1:
            self.legend = self.timePlot.addLegend()

        pens = self.get_plot_pens(subchannel_count)
        for pen, subchannel_name in zip(pens, channel_info.subchannel_names):
            curve = self.timePlot.plot(pen=pen, name=subchannel_name)
            self.time_curves.append(curve)

        timeAxis = self.timePlot.getAxis('left')
        fftAxis = self.fftPlot.getAxis('left')
        if channel_info.unit_scale is None:
            timeAxis.setScale(1.0)
            timeAxis.setLabel(channel_info.unit_str, units="")
            fftAxis.setScale(1.0)
            fftAxis.setLabel(channel_info.unit_str, units="")
        else:
            timeAxis.setScale(channel_info.unit_scale)
            timeAxis.setLabel("", units=channel_info.unit_str)
            fftAxis.setScale(channel_info.unit_scale)
            fftAxis.setLabel("", units=channel_info.unit_str)

        if self.plot_mean:
            plot_rate = channel_info.rate / channel_info.downsample_factor
            factor = math.ceil(plot_rate)
            if factor > 1:
                self.timePlot.setDownsampling(factor, False, "mean")
            else:
                self.timePlot.setDownsampling(False, False, "mean")
        else:
            self.timePlot.setDownsampling(False, False, "mean")

        # add region for FFT size
        if channel_info.fft_shortened:
            duration = channel_info.fft_sample_len / channel_info.rate
            lr = pyqtgraph.LinearRegionItem([-duration, 0], movable=False)
            self.timePlot.addItem(lr)

        self.restore_plot_range(index)
        self.last_plot_range_channel_index = index

    def fft_subchannel_changed(self, _junk=None):
        self.fft_curve.clear()
        if self.calc_process:
            channel_index = self.graphChannelComboBox.currentIndex()
            subchannel_index = self.fftSubchannelComboBox.currentIndex()
            self.calc_process.plot_change(channel_index, subchannel_index)

    def save_plot_range(self, index):
        save_dict = self.saved_plot_ranges.setdefault(index, {})

        time_vb = self.timePlot.getViewBox()
        time_autorange = time_vb.autoRangeEnabled()
        time_range = time_vb.targetRange()
        save_dict['time'] = (time_autorange, time_range)

        if self.fft_curve.getData()[0] is not None:
            fft_vb = self.fftPlot.getViewBox()
            fft_autorange = fft_vb.autoRangeEnabled()
            fft_range = fft_vb.targetRange()
            save_dict['fft'] = (fft_autorange, fft_range)

    def restore_plot_range(self, index):
        save_dict = self.saved_plot_ranges.get(index, {})

        def restore(vb, autorange, targetrange):
            x_autorange, y_autorange = autorange

            # restore the autorange
            vb.enableAutoRange(x=x_autorange, y=y_autorange)

            if not x_autorange:
                vb.setXRange(*targetrange[0], update=False, padding=0.0)
            if not y_autorange:
                vb.setYRange(*targetrange[1], update=False, padding=0.0)

        if 'time' in save_dict:
            restore(self.timePlot.getViewBox(), *save_dict['time'])
        else:
            restore(self.timePlot.getViewBox(), [True, True], [])

        if 'fft' in save_dict:
            restore(self.fftPlot.getViewBox(), *save_dict['fft'])
        else:
            restore(self.fftPlot.getViewBox(), [True, True], [])

    def rgb_set(self, color):
        if self.auto_rgb:
            try:
                rgb_widget = self.rgb_widgets[0]
                rgb_widget.set_color_from_button(color)
            except IndexError:
                pass

    def rgb_connected(self):
        if self.device_info['supports_radio']:
            self.rgb_set((0, 255, 255))  # cyan
        else:
            self.rgb_set((0, 0, 255))  # blue

    def rgb_disconnected(self):
        self.rgb_set((255, 0, 0))  # red

    def rgb_streaming(self):
        if self.device_info['supports_radio']:
            pass
        else:
            self.rgb_set((0, 255, 0))  # green

    def rgb_remote_connected(self):
        self.rgb_set((0, 0, 255))  # blue

    def rgb_remote_disconnected(self):
        self.rgb_set((0, 255, 255))  # cyan

    def rgb_remote_streaming(self):
        self.rgb_set((0, 255, 0))  # green

    def set_is_shown(self, is_shown):
        if self.calc_process:
            self.calc_process.set_is_shown(is_shown)
        self.is_shown = is_shown
