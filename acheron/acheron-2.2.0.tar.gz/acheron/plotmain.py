import bisect
import datetime
import functools
import logging
import math
import os
import subprocess
import sys
import tempfile
import threading
import urllib.parse

import diskcache
from PySide2 import QtCore, QtGui, QtSvg, QtWidgets

import asphodel
import hyperborea.alert
import hyperborea.download
from hyperborea.preferences import read_bool_setting
from hyperborea.preferences import read_int_setting
from hyperborea.preferences import write_bool_setting
import hyperborea.upload

from .ui_plotmain import Ui_PlotMainWindow
from .about import AboutDialog
from .device_tab import DeviceTab
from .connect_tcp_dialog import ConnectTCPDialog
from .download_firmware_dialog import DownloadFirmwareDialog
from .preferences import PreferencesDialog, set_style
from .tcp_scan_dialog import TCPScanDialog

logger = logging.getLogger(__name__)


def find_and_open_tcp_device(location_string):
    devices = asphodel.find_tcp_devices()
    for device in devices:
        device_location_string = device.get_location_string()
        if device_location_string == location_string:
            device.open()
            return device


def find_and_open_usb_device(location_string):
    devices = asphodel.find_usb_devices()
    for device in devices:
        device_location_string = device.get_location_string()
        if device_location_string == location_string:
            device.open()
            return device


def connect_and_open_tcp_device(host, port, timeout, serial):
    device = asphodel.create_tcp_device(host, port, timeout, serial)
    device.open()
    return device


class PlotMainWindow(QtWidgets.QMainWindow, Ui_PlotMainWindow):
    device_check_finished = QtCore.Signal(object)
    connect_tcp_info_ready = QtCore.Signal(object)

    def __init__(self, proxy_manager, parent=None):
        super().__init__(parent)

        self.disable_streaming = False
        self.disable_archiving = False

        # these will be created later, if necessary
        self.upload_manager = None
        self.alert_manager = None

        self.rate_update_interval = 0.5
        self.rate_average_period = 5.0
        self.rate_average_period_ms = int(self.rate_average_period * 1000)

        self.settings = QtCore.QSettings()
        self.update_style()

        self.load_base_dir()
        self.create_diskcache()

        self.proxy_manager = proxy_manager
        self.proxy_lock = threading.Lock()  # locks access to self.proxies
        self.proxies = {}  # location string key, proxy value
        self.device_tabs = {}  # serial number key, widget value
        self.disconnected_tabs_lock = threading.Lock()
        self.disconnected_tabs = {}  # widget key, reconnect_info value

        self.finished = threading.Event()
        self.should_scan = threading.Event()

        self.tab_widgets = []  # list of tab widgets, in display order
        self.tab_sort_order = []  # matched to self.tab_widgets
        self.shown_tab = None

        self.rf_power_panels = {}  # key=panel, value=enabled boolean

        self.update_progress_lock = threading.Lock()

        self.setupUi(self)
        self.extra_ui_setup()
        self.setup_logo()

        self.setup_callbacks()
        self.setup_update_actions()

        self.create_upload_manager()
        self.create_alert_manager()

        self.collapsed = read_bool_setting(self.settings, "Collapsed", False)

        if sys.platform == "darwin":
            # I couldn't figure out how to make menu work natively
            self.menubar.setNativeMenuBar(False)

        # restore window geometry
        geometry = self.settings.value('Geometry', b'')
        self.restoreGeometry(geometry)

        # schedule the initial connect for the beginning of the main loop
        QtCore.QTimer.singleShot(0, self.initial_device_connect)

    def load_base_dir(self):
        self.base_dir = self.settings.value("BasePath")
        if not self.base_dir:
            documents_path = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.DocumentsLocation)
            app_name = QtWidgets.QApplication.applicationName()
            self.base_dir = os.path.join(documents_path, app_name + " Data")

    def create_diskcache(self):
        self.diskcache_dir = self.settings.value("DiskCachePath")
        if not self.diskcache_dir:
            self.diskcache_dir = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.CacheLocation)
        self.diskcache = diskcache.Cache(self.diskcache_dir, size_limit=100e6)

    def create_upload_manager(self):
        if self.upload_manager is not None:
            # remove the old one
            self.upload_manager.stop()
            self.upload_manager = None

        self.settings.beginGroup("Upload")
        upload_enabled = read_bool_setting(self.settings, "Enabled", False)
        delete_original = read_bool_setting(self.settings, "DeleteOriginal",
                                            False)
        upload_options = {
            'delete_after_upload': delete_original,
            's3_bucket': self.settings.value("S3Bucket"),
            'key_prefix': self.settings.value("Directory"),
            'access_key_id': self.settings.value("AccessKeyID"),
            'secret_access_key': self.settings.value("SecretAccessKey"),
            'aws_region': self.settings.value("AWSRegion")}
        self.settings.endGroup()

        if upload_enabled:
            try:
                self.upload_manager = hyperborea.upload.UploadManager(
                    self.base_dir,
                    rate_update_interval=self.rate_update_interval,
                    rate_average_period=self.rate_average_period,
                    **upload_options)
            except Exception:
                msg = "Error starting uploader. Check upload configuration."
                logger.exception(msg)
                QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                               self.tr(msg))

        if self.upload_manager:
            self.uploadRateLabel.setVisible(True)
            self.uploadProgress.setVisible(False)  # hide when inactive
            self.uploadNameLabel.setVisible(True)
            self.uploadRateLabel.setText("0.0 kB/s")
            self.uploadNameLabel.setText("Checking upload configuration")

            self.upload_manager.rate_status.connect(self.rate_status_cb)
            self.upload_manager.upload_status.connect(self.upload_status_cb)
            self.upload_manager.started.connect(self.upload_manager_started)
            self.upload_manager.error.connect(self.upload_manager_error)
        else:
            # no upload configured, hide associated widgets
            self.uploadRateLabel.setVisible(False)
            self.uploadProgress.setVisible(False)
            self.uploadNameLabel.setVisible(False)

    def create_alert_manager(self):
        if self.alert_manager is not None:
            # remove the old one
            self.alert_manager.stop()
            self.alert_manager = None

        self.settings.beginGroup("AlertEmail")
        email_enabled = read_bool_setting(self.settings, "Enabled", False)

        email_options = {
            'from_address': self.settings.value("FromAddress"),
            'to_address': self.settings.value("ToAddress"),
            'smtp_host': self.settings.value("SMTPHost"),
            'smtp_port': read_int_setting(self.settings, "SMTPPort", 587),
            'use_auth': read_bool_setting(self.settings, "UseAuth", True),
            'smtp_user': self.settings.value("SMTPUser"),
            'smtp_password': self.settings.value("SMTPPassword")}

        security = self.settings.value("Security")
        if security:
            security = security.strip()
        if security == "STARTTLS":
            email_options['security'] = 'starttls'
        elif security == "SSL":
            email_options['security'] = 'ssl'
        elif security == "None":
            email_options['security'] = ''
        else:
            email_options['security'] = 'starttls'
        self.settings.endGroup()

        if email_enabled:
            try:
                self.alert_manager = hyperborea.alert.AlertManager(
                    email_options)
            except Exception:
                msg = "Error with email configuration!"
                logger.exception(msg)
                QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                               self.tr(msg))

    def setup_logo(self):
        self.stackedWidget.setCurrentIndex(1)
        self.logo = QtSvg.QSvgWidget(":/logo.svg")
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                            QtWidgets.QSizePolicy.Ignored)
        self.logo.setSizePolicy(size_policy)

        def resizeEvent(event):
            size = event.size()
            margins = self.logoLayout.contentsMargins()

            if size.width() == size.height():
                return

            full_width = size.width() + margins.left() + margins.right()
            full_height = size.height() + margins.top() + margins.bottom()

            d = min(full_width, full_height)
            top = math.ceil((full_height - d) / 2)
            bottom = math.floor((full_height - d) / 2)
            left = math.ceil((full_width - d) / 2)
            right = math.floor((full_width - d) / 2)
            self.logoLayout.setContentsMargins(left, top, right, bottom)
        self.logo.resizeEvent = resizeEvent

        self.logoLayout.addWidget(self.logo)

    def extra_ui_setup(self):
        self.warningLabel.setVisible(False)

        self.actionEnableRFPower.setEnabled(False)
        self.actionDisableRFPower.setEnabled(False)

        self.spacer = QtWidgets.QWidget()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        self.spacer.setSizePolicy(size_policy)
        self.toolBar.insertWidget(self.actionRescanUSB, self.spacer)

        if not asphodel.nativelib.usb_devices_supported:
            self.actionRescanUSB.setEnabled(False)
        if not asphodel.nativelib.tcp_devices_supported:
            self.actionFindTCPDevices.setEnabled(False)
            self.actionConnectTCPDevice.setEnabled(False)

        self.update_datetime_label()

        if read_bool_setting(self.settings, "ClosableTabs", False):
            self.actionClosableTabs.setChecked(True)
            self.tabWidget.setTabsClosable(True)

        self.update_progress = QtWidgets.QProgressDialog("", "", 0, 100)
        self.update_progress.setLabelText(self.tr(""))
        self.update_progress.setWindowTitle(self.tr("Check for Update"))
        self.update_progress.setCancelButton(None)
        self.update_progress.setWindowModality(QtCore.Qt.WindowModal)
        self.update_progress.setMinimumDuration(0)
        self.update_progress.setAutoReset(False)
        self.update_progress.reset()

        self.actionAbout.setIcon(QtGui.QIcon.fromTheme("about"))
        self.actionConnectTCPDevice.setIcon(QtGui.QIcon.fromTheme(
            "earth_network"))
        self.actionDisableRFPower.setIcon(QtGui.QIcon.fromTheme(
            "antenna_stop"))
        self.actionDownloadFirmware.setIcon(QtGui.QIcon.fromTheme("install"))
        self.actionExit.setIcon(QtGui.QIcon.fromTheme("exit"))
        self.actionEnableRFPower.setIcon(QtGui.QIcon.fromTheme("antenna_play"))
        self.actionFindTCPDevices.setIcon(QtGui.QIcon.fromTheme("plug_lan"))
        self.actionMarkDirectory.setIcon(QtGui.QIcon.fromTheme("folder_up"))
        self.actionMarkFiles.setIcon(QtGui.QIcon.fromTheme("document_up"))
        self.actionPreferences.setIcon(QtGui.QIcon.fromTheme("preferences"))
        self.actionRescanUSB.setIcon(QtGui.QIcon.fromTheme("plug_usb"))
        self.actionUpdateCurrentBranch.setIcon(QtGui.QIcon.fromTheme(
            "branch_element_new"))
        self.actionUpdateLatestStable.setIcon(QtGui.QIcon.fromTheme("branch"))
        self.actionUpdateSpecificBranch.setIcon(QtGui.QIcon.fromTheme(
            "branch_view"))
        self.actionUpdateSpecificCommit.setIcon(QtGui.QIcon.fromTheme(
            "symbol_hash"))
        self.menuCheckForUpdates.setIcon(QtGui.QIcon.fromTheme(
            "cloud_computing_download"))

    def setup_callbacks(self):
        self.actionEnableRFPower.triggered.connect(self.enable_rf_power_cb)
        self.actionDisableRFPower.triggered.connect(self.disable_rf_power_cb)

        self.actionRescanUSB.triggered.connect(self.rescan_usb_devices)
        self.actionFindTCPDevices.triggered.connect(self.find_tcp_devices)
        self.actionConnectTCPDevice.triggered.connect(self.connect_tcp_device)
        self.actionDisableStreaming.triggered.connect(
            self.set_disable_streaming)
        self.actionDisableArchiving.triggered.connect(
            self.set_disable_archiving)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionChannelTable.triggered.connect(self.show_channel_table)
        self.actionShowLogs.triggered.connect(self.show_log_dir)
        self.actionPreferences.triggered.connect(self.show_preferences)
        self.actionClosableTabs.triggered.connect(self.closable_tabs_cb)

        self.device_check_thread = threading.Thread(
            target=self.device_check_thread_run)
        self.device_check_thread.start()
        self.device_check_finished.connect(self.device_check_finished_cb)

        self.clock_timer = QtCore.QTimer(self)
        self.clock_timer.timeout.connect(self.update_datetime_label)
        self.clock_timer.start(1000)  # 1 second intervals

        self.upload_timeout_timer = QtCore.QTimer(self)
        self.upload_timeout_timer.setSingleShot(True)
        self.upload_timeout_timer.timeout.connect(self.upload_timeout_cb)

        self.destroyed.connect(self.destroyed_cb)

        self.tabWidget.tabCloseRequested.connect(self.tab_close_requested)
        self.tabWidget.currentChanged.connect(self.current_tab_changed_cb)

        self.actionDownloadFirmware.triggered.connect(
            self.download_firmware)
        self.firmware_downloader = hyperborea.download.Downloader()
        self.firmware_downloader.completed.connect(
            self.firmware_download_completed)
        self.firmware_downloader.error.connect(self.firmware_download_error)
        self.firmware_finder = hyperborea.download.FirmwareFinder()
        self.firmware_finder.completed.connect(self.firmware_finder_completed)
        self.firmware_finder.error.connect(self.firmware_finder_error)

        self.actionUpdateLatestStable.triggered.connect(
            self.update_latest_stable)
        self.actionUpdateCurrentBranch.triggered.connect(
            self.update_current_branch)
        self.actionUpdateSpecificBranch.triggered.connect(
            self.update_specific_branch)
        self.actionUpdateSpecificCommit.triggered.connect(
            self.update_specific_commit)

        self.update_progress_timer = QtCore.QTimer(self)
        self.update_progress_timer.timeout.connect(self.update_progress_cb)

        self.software_finder = hyperborea.download.SoftwareFinder()
        self.software_finder.completed.connect(self.update_finder_completed)
        self.software_finder.error.connect(self.update_finder_error)
        self.ref_finder = hyperborea.download.RefFinder()
        self.ref_finder.completed.connect(self.ref_finder_completed)
        self.ref_finder.error.connect(self.ref_finder_error)
        self.software_downloader = hyperborea.download.Downloader()
        self.software_downloader.completed.connect(
            self.software_download_completed)
        self.software_downloader.error.connect(self.software_download_error)

        self.actionMarkDirectory.triggered.connect(self.mark_directory)
        self.actionMarkFiles.triggered.connect(self.mark_files)

        self.next_tab_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_PageDown), self)
        self.next_tab_shortcut.activated.connect(self.next_tab)
        self.prev_tab_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_PageUp), self)
        self.prev_tab_shortcut.activated.connect(self.prev_tab)

        self.connect_tcp_info_ready.connect(self.connect_tcp_device_cb)

    def setup_update_actions(self):
        is_frozen = getattr(sys, 'frozen', False)

        valid_info = False
        if is_frozen:
            # load the build_info.txt
            main_dir = os.path.dirname(sys.executable)
            build_info_filename = os.path.join(main_dir, "build_info.txt")
            try:
                with open(build_info_filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    self.branch_name = lines[0].strip()
                    self.commit_hash = lines[1].strip()
                    self.build_key = lines[2].strip()
                    valid_info = True
            except Exception:
                logger.exception('Could not read build_info.txt')

        if not valid_info:
            self.menuCheckForUpdates.setEnabled(False)
            self.menuCheckForUpdates.setTitle(self.tr("Not Updatable"))
            self.actionUpdateLatestStable.setEnabled(False)
            self.actionUpdateCurrentBranch.setEnabled(False)
            self.actionUpdateSpecificBranch.setEnabled(False)
            self.actionUpdateSpecificCommit.setEnabled(False)
        else:
            if self.branch_name == "master":
                # master is latest stable
                self.actionUpdateCurrentBranch.setEnabled(False)
                self.actionUpdateCurrentBranch.setVisible(False)
            else:
                action_str = self.tr("Latest {}").format(self.branch_name)
                self.actionUpdateCurrentBranch.setText(action_str)

    def find_update(self, branch=None, commit=None):
        self.update_progress.setMinimum(0)
        self.update_progress.setMaximum(0)
        self.update_progress.setValue(0)
        self.update_progress.setLabelText(self.tr("Checking for update..."))
        self.update_progress.forceShow()

        self.software_finder.find_software("acheron", self.build_key, branch,
                                           commit)

    def update_finder_error(self, error_str):
        self.update_progress.reset()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)

    def update_finder_completed(self, params):
        self.update_progress.reset()
        url, commit, ready = params

        if commit is not None and commit == self.commit_hash:
            logger.info("Up to date with commit %s", commit)
            QtWidgets.QMessageBox.information(
                self, self.tr("Up to date"),
                self.tr("Already running this version"))
            return

        if not ready:
            logger.info("Update is not ready")
            QtWidgets.QMessageBox.information(
                self, self.tr("Update not ready"),
                self.tr("Update is not ready"))
            return

        # ask if the user wants to proceed
        ret = QtWidgets.QMessageBox.question(
            self, self.tr("Update?"), self.tr("Update available. Update now?"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ret != QtWidgets.QMessageBox.Yes:
            return

        logger.info("Downloading update from %s", url)

        self.update_progress.setMinimum(0)
        self.update_progress.setMaximum(0)
        self.update_progress.setValue(0)
        self.update_progress.setLabelText(self.tr("Downloading update..."))
        self.update_progress.forceShow()

        self.update_progress_written = 0
        self.update_progress_total = 0

        fd, filename = tempfile.mkstemp(".exe", "setup-", text=False)
        file = os.fdopen(fd, "wb")
        file.filename = filename
        self.software_downloader.start_download(url, file,
                                                self.update_progress_func)

        self.update_progress_timer.start(20)  # 20 milliseconds

    def update_progress_func(self, written_bytes, total_length):
        with self.update_progress_lock:
            self.update_progress_total = total_length
            self.update_progress_written = written_bytes

    def update_progress_cb(self):
        with self.update_progress_lock:
            if self.update_progress_total != 0:
                self.update_progress.setMinimum(0)
                self.update_progress.setMaximum(self.update_progress_total)
                self.update_progress.setValue(self.update_progress_written)

    def software_download_error(self, file, error_str):
        self.update_progress_timer.stop()
        self.update_progress.reset()
        file.close()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)
        os.unlink(file.filename)

    def software_download_completed(self, file):
        self.update_progress_timer.stop()
        self.update_progress.reset()
        file.close()

        # stop the managers
        if self.upload_manager:
            self.upload_manager.stop()
        if self.alert_manager:
            self.alert_manager.stop()

        # close all device tabs
        while True:
            if not self.tab_widgets:
                break
            widget = self.tab_widgets[0]
            self.close_tab(widget)

        # run the intstaller
        subprocess.Popen([file.filename, '/silent', "/DeleteInstaller=Yes",
                          "/SP-", "/SUPPRESSMSGBOXES", "/NORESTART",
                          "/NOCANCEL"])

        # close the application (though installer will force kill regardless)
        self.close()

    def update_latest_stable(self):
        self.find_update(branch="master")

    def update_current_branch(self):
        self.find_update(branch=self.branch_name)

    def update_specific_branch(self):
        self.update_progress.setMinimum(0)
        self.update_progress.setMaximum(0)
        self.update_progress.setValue(0)
        self.update_progress.setLabelText(self.tr("Collecting branches..."))
        self.update_progress.forceShow()

        self.ref_finder.get_software_refs("acheron")

    def ref_finder_error(self, error_str):
        self.ref_finder_completed([])

    def ref_finder_completed(self, refs):
        self.update_progress.reset()

        default_branch = self.branch_name
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
            label = self.tr("Branch:")
        else:
            label = self.tr("No list of branches!\Branch:")

        branch, ok = QtWidgets.QInputDialog.getItem(
            self, self.tr("Branch"), label, branch_choices, 0, True)
        if not ok:
            return

        branch = branch.strip()

        self.find_update(branch=branch)

    def update_specific_commit(self):
        commit, ok = QtWidgets.QInputDialog.getText(
            self, self.tr("Commit"), self.tr("Commit:"),
            QtWidgets.QLineEdit.Normal, "")
        if not ok:
            return

        commit = commit.strip()

        self.find_update(commit=commit)

    def download_firmware(self):
        dialog = DownloadFirmwareDialog(parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        results = dialog.get_results()

        self.firmware_finder.find_firmware(build_type=None, **results)

    def firmware_finder_error(self, error_str):
        self.update_progress.reset()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)

    def get_firmware_save_file(self, default_name):
        # find the directory from settings
        directory = self.settings.value("fileSaveDirectory")
        if directory and type(directory) == str:
            if not os.path.isdir(directory):
                directory = None

        if not directory:
            directory = ""

        file_and_dir = os.path.join(directory, default_name)

        caption = self.tr("Save Firmware File")
        file_filter = self.tr("Firmware Files (*.firmware);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getSaveFileName(
            self, caption, file_and_dir, file_filter)
        output_path = val[0]

        if output_path:
            # save the directory
            output_dir = os.path.dirname(output_path)
            self.settings.setValue("fileSaveDirectory", output_dir)
            return output_path
        else:
            return None

    def firmware_finder_completed(self, build_urls):
        self.update_progress.reset()
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

        u = urllib.parse.urlparse(url)
        default_filename = os.path.basename(u.path)
        filename = self.get_firmware_save_file(default_filename)
        if not filename:
            return

        logger.info("Downloading firmware from %s", url)

        self.update_progress.setMinimum(0)
        self.update_progress.setMaximum(0)
        self.update_progress.setValue(0)
        self.update_progress.setLabelText(
            self.tr("Downloading firmware..."))
        self.update_progress.forceShow()

        self.update_progress_written = 0
        self.update_progress_total = 0

        file = open(filename, "wb")
        self.firmware_downloader.start_download(url, file,
                                                self.update_progress_func)

        self.update_progress_timer.start(20)  # 20 milliseconds

    def firmware_download_error(self, file, error_str):
        self.update_progress_timer.stop()
        self.update_progress.reset()
        file.close()
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), error_str)
        os.unlink(file.filename)

    def firmware_download_completed(self, file):
        self.update_progress_timer.stop()
        self.update_progress.reset()
        file.close()
        QtWidgets.QMessageBox.information(self, self.tr("Finished"),
                                          self.tr("Finished download"))

    def create_widget(self, serial_number, sort_location):
        # create a new device tab
        widget = DeviceTab(serial_number, self.base_dir, self.diskcache,
                           self, disable_streaming=self.disable_streaming,
                           disable_archiving=self.disable_archiving,
                           upload_manager=self.upload_manager,
                           alert_manager=self.alert_manager,
                           collapsed=self.collapsed)
        self.device_tabs[serial_number] = widget

        # find the insertion index
        index = bisect.bisect(self.tab_sort_order, sort_location)
        self.tab_sort_order.insert(index, sort_location)
        self.tab_widgets.insert(index, widget)
        self.tabWidget.insertTab(index, widget, self.tr("Connecting..."))
        if index == 0:
            self.tabWidget.setCurrentIndex(index)
        self.stackedWidget.setCurrentIndex(0)

        update_func = functools.partial(self.update_widget_text, widget)
        widget.name_update.connect(update_func)
        close_func = functools.partial(self.close_tab, widget)
        widget.close_pressed.connect(close_func)
        widget.collapsed_set.connect(self.collapsed_set)

    def create_proxy(self, proxy_args, location_string, serial_number,
                     sort_location, reconnect_info=None):
        if serial_number not in self.device_tabs:
            self.create_widget(serial_number, sort_location)

        proxy = self.proxy_manager.new_proxy(serial_number, *proxy_args)
        connected = functools.partial(self.proxy_connected, proxy,
                                      serial_number)
        proxy.connected.connect(connected)
        disconnected = functools.partial(
            self.proxy_disconnected, proxy, location_string, serial_number,
            reconnect_info)
        proxy.disconnected.connect(disconnected)
        proxy.open_connection()
        with self.proxy_lock:
            self.proxies[location_string] = proxy

    def collect_new_usb_device_keys(self):
        with self.proxy_lock:
            location_strings = self.proxies.copy().keys()
        keys = []
        for device in asphodel.find_usb_devices():
            location_str = device.get_location_string()
            if location_str not in location_strings:
                # found one we don't already have
                try:
                    device.open()
                    serial_number = device.get_serial_number()
                except asphodel.AsphodelError:
                    continue
                finally:
                    device.close()

                # SN first in the tuple for sorting reasons
                keys.append((serial_number, location_str))
        return keys

    def initial_device_connect(self):
        if asphodel.nativelib.usb_devices_supported:
            usb_keys = self.collect_new_usb_device_keys()
            for i, (sn, location_str) in enumerate(sorted(usb_keys)):
                proxy_args = [find_and_open_usb_device, location_str]
                self.create_proxy(proxy_args, location_str, sn, i + 1)

            # look for TCP devices if there weren't any USB ones
            if len(usb_keys) == 0 and asphodel.nativelib.tcp_devices_supported:
                # find if there are any TCP devices
                tcp_devices = asphodel.find_tcp_devices()

                # but only show the dialog if there are some
                if tcp_devices:
                    chosen = self.choose_tcp_devices(tcp_devices)
                    tcp_keys = self.get_tcp_device_keys(chosen)
                    for i, (sn, location_str) in enumerate(sorted(tcp_keys)):
                        proxy_args = [find_and_open_tcp_device, location_str]
                        self.create_proxy(proxy_args, location_str, sn, i + 1)
        elif asphodel.nativelib.tcp_devices_supported:
            # bring up TCP scan dialog (even if empty)
            self.find_tcp_devices()
        else:
            # no TCP or USB supported by DLL
            msg = "Asphodel library does not support USB or TCP devices"
            logging.warning(msg)
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"),
                                          self.tr(msg))

    def rescan_usb_devices(self):
        # reset sort locations
        self.tab_sort_order = [0] * len(self.tab_sort_order)

        keys = self.collect_new_usb_device_keys()

        for i, (serial_number, location_str) in enumerate(sorted(keys)):
            proxy_args = [find_and_open_usb_device, location_str]
            self.create_proxy(proxy_args, location_str, serial_number, i + 1)

    def get_tcp_device_keys(self, devices):
        keys = []
        for device in devices:
            adv = device.tcp_get_advertisement()
            if adv.connected:
                continue
            location_str = device.get_location_string()
            serial_number = adv.serial_number
            # SN first in the tuple for sorting reasons
            keys.append((serial_number, location_str))
        return keys

    def choose_tcp_devices(self, devices):
        # sort into connected and unconnected by location string
        def get_location_strings():
            with self.proxy_lock:
                return self.proxies.copy().keys()

        def rescan():
            try:
                return asphodel.find_tcp_devices()
            except Exception:
                return []

        dialog = TCPScanDialog(devices, get_location_strings, rescan,
                               parent=self)

        ret = dialog.exec_()
        if ret == 0:
            return []  # user cancelled

        return dialog.get_selected_devices()

    def find_tcp_devices(self):
        # reset sort locations
        self.tab_sort_order = [0] * len(self.tab_sort_order)

        try:
            devices = asphodel.find_tcp_devices()
        except Exception:
            devices = []
        chosen = self.choose_tcp_devices(devices)
        keys = self.get_tcp_device_keys(chosen)

        for i, (serial_number, location_str) in enumerate(sorted(keys)):
            proxy_args = [find_and_open_tcp_device, location_str]
            self.create_proxy(proxy_args, location_str, serial_number, i + 1)

    def connect_tcp_device(self):
        dialog = ConnectTCPDialog(parent=self)
        ret = dialog.exec_()
        if ret == 0:
            return  # user cancelled

        results = dialog.get_results()
        results['timeout'] = 1000

        t = threading.Thread(target=self.connect_tcp_device_run,
                             args=(results,))
        t.start()

    def connect_tcp_device_run(self, results):
        try:
            device = asphodel.create_tcp_device(
                results['hostname'], results['port'], results['timeout'],
                results['serial_number'])
            device.open()
            device.close()
        except asphodel.AsphodelError:
            logger.exception("Could not connect to TCP device.")
            self.connect_tcp_info_ready.emit({})
            return

        adv = device.tcp_get_advertisement()
        serial_number = adv.serial_number
        location_string = device.get_location_string()

        results['serial_number'] = serial_number
        results['location_string'] = location_string
        self.connect_tcp_info_ready.emit(results)

    def connect_tcp_device_cb(self, results):
        if not results:
            QtWidgets.QMessageBox.critical(
                self, self.tr("Error"), self.tr("Could not connect to device"))
            return

        # reset sort locations
        self.tab_sort_order = [0] * len(self.tab_sort_order)

        proxy_args = [connect_and_open_tcp_device, results['hostname'],
                      results['port'], results['timeout'],
                      results['serial_number']]

        def reconnect_info():
            try:
                device = asphodel.create_tcp_device(
                    results['hostname'], results['port'], results['timeout'],
                    results['serial_number'])
                device.open()
                device.close()
            except asphodel.AsphodelError:
                return None
            location_string = device.get_location_string()
            return (results['serial_number'], location_string, proxy_args,
                    reconnect_info)

        self.create_proxy(proxy_args, results['location_string'],
                          results['serial_number'], 1, reconnect_info)

    def device_check_finished_cb(self, results):
        with self.disconnected_tabs_lock:
            if not self.disconnected_tabs:
                return  # no devices are disconnected

        for sn, location_str, proxy_args, reconnect_info in results:
            if sn in self.device_tabs:
                # found one to reconnect
                self.create_proxy(proxy_args, location_str, sn, 0,
                                  reconnect_info)

    def device_check_thread_run(self):
        while True:
            if self.finished.wait(timeout=1.5):
                return  # done

            if not self.should_scan.is_set():
                continue

            results = []  # sn, location_str, proxy_args, reconnect_info

            # look for USB devices
            if asphodel.nativelib.usb_devices_supported:
                usb_keys = self.collect_new_usb_device_keys()
                for sn, location_str in usb_keys:
                    proxy_args = [find_and_open_usb_device, location_str]
                    results.append((sn, location_str, proxy_args, None))

            # look for TCP devices
            if asphodel.nativelib.tcp_devices_supported:
                with self.proxy_lock:
                    location_strings = self.proxies.copy().keys()

                tcp_devices = asphodel.find_tcp_devices()
                tcp_keys = self.get_tcp_device_keys(tcp_devices)

                for sn, location_str in tcp_keys:
                    if location_str not in location_strings:
                        proxy_args = [find_and_open_tcp_device, location_str]
                        results.append((sn, location_str, proxy_args, None))

            with self.disconnected_tabs_lock:
                values = [f for f in self.disconnected_tabs.values() if f]
            for reconnect_info in values:
                result = reconnect_info()
                if result:
                    results.append(result)

            if results:
                self.device_check_finished.emit(results)

    def proxy_connected(self, proxy, serial_number):
        if serial_number in self.device_tabs:
            widget = self.device_tabs[serial_number]
            with self.disconnected_tabs_lock:
                if widget in self.disconnected_tabs:
                    del self.disconnected_tabs[widget]
                if not self.disconnected_tabs:
                    self.should_scan.clear()
            widget.set_proxy(proxy)

    def proxy_disconnected(self, proxy, location_string, serial_number,
                           reconnect_info):
        # tab handles its own disconnect

        # remove the proxy from the proxies list
        with self.proxy_lock:
            if self.proxies.get(location_string) == proxy:
                del self.proxies[location_string]
        widget = self.device_tabs.get(serial_number, None)
        if widget:
            with self.disconnected_tabs_lock:
                self.disconnected_tabs[widget] = reconnect_info
            self.should_scan.set()

    def closeEvent(self, event):
        geometry = self.saveGeometry()
        self.settings.setValue('Geometry', geometry)

        self.finished.set()
        if self.upload_manager:
            self.upload_manager.stop()
        if self.alert_manager:
            self.alert_manager.stop()

        # notify widgets
        for widget in self.tab_widgets:
            widget.stop_and_close()

        QtWidgets.QWidget.closeEvent(self, event)

    def destroyed_cb(self, _junk=None):
        self.finished.set()
        if self.upload_manager:
            self.upload_manager.stop()
        if self.alert_manager:
            self.alert_manager.stop()

    def update_widget_text(self, widget, text):
        try:
            index = self.tab_widgets.index(widget)
            self.tabWidget.setTabText(index, text)
        except ValueError:
            pass

    def close_tab(self, widget):
        widget.stop_and_close()

        # find the serial number from the widget
        serials = [k for k, v in self.device_tabs.items() if v == widget]
        for serial_number in serials:
            del self.device_tabs[serial_number]

        with self.disconnected_tabs_lock:
            if widget in self.disconnected_tabs:
                del self.disconnected_tabs[widget]
            if not self.disconnected_tabs:
                self.should_scan.clear()

        try:
            if self.shown_tab == widget:
                self.shown_tab = None
            index = self.tab_widgets.index(widget)
            self.tab_widgets.pop(index)
            self.tab_sort_order.pop(index)
            self.tabWidget.removeTab(index)
        except ValueError:
            pass

        if len(self.tab_widgets) == 0:
            self.stackedWidget.setCurrentIndex(1)

    def show_tab(self, widget, src=None):  # called from a radio/remote panel
        if src and self.tabWidget.currentWidget() != src:
            return  # source is not currently displayed
        self.tabWidget.setCurrentWidget(widget)

    def create_tab(self, proxy, sn, stream_list):  # called from a radio panel
        # create a new device tab
        widget = DeviceTab(sn, self.base_dir, self.diskcache, self,
                           stream_list, self.disable_streaming,
                           self.disable_archiving, self.upload_manager,
                           self.alert_manager, collapsed=self.collapsed)

        # find the insertion index
        index = len(self.tab_widgets)
        self.tab_sort_order.append(0)
        self.tab_widgets.append(widget)
        self.tabWidget.insertTab(index, widget, self.tr("Connecting..."))

        update_func = functools.partial(self.update_widget_text, widget)
        widget.name_update.connect(update_func)
        close_func = functools.partial(self.close_tab, widget)
        widget.close_pressed.connect(close_func)
        widget.collapsed_set.connect(self.collapsed_set)

        widget.set_proxy(proxy)

        return widget

    def register_rf_power_panel(self, panel):
        def connect_callback(status):
            self.rf_power_panels[panel] = status
            self.update_rf_power_buttons()

        def status_callback(status):
            if panel in self.rf_power_panels:
                self.rf_power_panels[panel] = status
            self.update_rf_power_buttons()

        def disconnect_callback():
            if panel in self.rf_power_panels:
                del self.rf_power_panels[panel]
                self.update_rf_power_buttons()

        # NOTE: status and connect do the same thing
        panel.connected_signal.connect(connect_callback)
        panel.status_signal.connect(status_callback)
        panel.disconnected_signal.connect(disconnect_callback)

    def update_rf_power_buttons(self):
        values = list(self.rf_power_panels.values())

        enabled_count = values.count(True)
        disabled_count = values.count(False)

        enable_text = self.tr("Enable RF Power ({})").format(disabled_count)
        self.actionEnableRFPower.setText(enable_text)
        self.actionEnableRFPower.setEnabled(disabled_count > 0)

        disable_text = self.tr("Disable RF Power ({})").format(enabled_count)
        self.actionDisableRFPower.setText(disable_text)
        self.actionDisableRFPower.setEnabled(enabled_count > 0)

    def enable_rf_power_cb(self):
        for panel, enabled in self.rf_power_panels.items():
            if not enabled:
                panel.enable_callback()

    def disable_rf_power_cb(self):
        for panel, enabled in self.rf_power_panels.items():
            if enabled:
                panel.disable_callback()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def get_htmL_dir(self):
        is_frozen = getattr(sys, 'frozen', False)
        if is_frozen:
            # load the build_info.txt
            return os.path.join(os.path.dirname(sys.executable), "html")
        else:
            return os.path.join(os.path.dirname(__file__), "html")

    def show_channel_table(self):
        filename = os.path.join(self.get_htmL_dir(), "asphodel_channels.html")
        url = QtCore.QUrl.fromLocalFile(filename)
        QtGui.QDesktopServices.openUrl(url)

    def show_log_dir(self):
        logdir = os.path.abspath(QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.DataLocation))
        logfile = os.path.join(logdir, "main.log")

        if sys.platform == "win32":
            subprocess.Popen(['explorer', '/select,', logfile])
        elif sys.platform == "darwin":
            args = [
                "osascript",
                "-e", 'tell application "Finder"',
                "-e", "activate",
                "-e", f'select POSIX file "{logfile}"',
                "-e", "end tell",
            ]
            subprocess.Popen(args)
        else:
            url = QtCore.QUrl.fromLocalFile(logdir)
            QtGui.QDesktopServices.openUrl(url)

    def show_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec_():
            self.load_base_dir()
            self.create_upload_manager()
            self.create_alert_manager()

            for tab_widget in self.tab_widgets[:]:
                if tab_widget in self.tab_widgets:
                    # hasn't been closed with another tab (like a WM)
                    tab_widget.update_preferences(
                        self.base_dir, self.upload_manager, self.alert_manager)
        self.update_style()

    def set_disable_streaming(self, _checked=False):
        self.disable_streaming = self.actionDisableStreaming.isChecked()
        for tab_widget in self.tab_widgets[:]:
            if tab_widget in self.tab_widgets:
                # hasn't been closed with another tab (like a WM)
                tab_widget.update_disable_streaming(self.disable_streaming)

    def set_disable_archiving(self, _checked=False):
        self.disable_archiving = self.actionDisableArchiving.isChecked()
        self.warningLabel.setVisible(self.disable_archiving)
        for tab_widget in self.tab_widgets[:]:
            if tab_widget in self.tab_widgets:
                # hasn't been closed with another tab (like a WM)
                tab_widget.update_disable_archiving(self.disable_archiving)

    def update_datetime_label(self):
        s = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.datetimeLabel.setText(s)

    def rate_status_cb(self, uploading, rate):
        if uploading:
            rate_str = "{:.1f} KB/s".format(rate / 1000)
        else:
            rate_str = "0.0 KB/s"
        self.uploadRateLabel.setText(rate_str)

    def upload_status_cb(self, filename, sent_bytes, total_bytes):
        self.uploadNameLabel.setText(filename)
        self.uploadProgress.setVisible(True)
        self.uploadProgress.setRange(0, total_bytes)
        self.uploadProgress.setValue(sent_bytes)
        if sent_bytes == total_bytes:
            self.upload_timeout_timer.start(self.rate_average_period_ms)
        else:
            self.upload_timeout_timer.stop()

    def upload_timeout_cb(self):
        self.uploadProgress.setVisible(False)
        self.uploadNameLabel.setText("Waiting for file to upload")

    def upload_manager_started(self):
        self.upload_timeout_cb()  # same logic as an upload finished

    def upload_manager_error(self):
        self.uploadNameLabel.setText("Error")
        msg = "Error connecting. Check upload configuration."
        QtWidgets.QMessageBox.critical(self, self.tr("Error"), self.tr(msg))

    def closable_tabs_cb(self):
        new_value = self.actionClosableTabs.isChecked()
        self.tabWidget.setTabsClosable(new_value)
        self.settings.setValue("ClosableTabs", 1 if new_value else 0)

    def tab_close_requested(self, index):
        widget = self.tab_widgets[index]
        widget.close_pressed.emit()

    def mark_directory(self):
        # ask the user for the file name
        output_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, self.tr("Select Directory"), self.base_dir)

        if not output_dir:
            return

        logger.info("Marking directory {}".format(output_dir))
        # search the directory for .upload files
        for root, _dirs, files in os.walk(output_dir):
            for name in files:
                if name.endswith(".apd"):
                    apd_filename = os.path.join(root, name)
                    logger.info("Marking file {}".format(apd_filename))
                    hyperborea.upload.mark_file_for_upload(apd_filename)
        if self.upload_manager:
            self.upload_manager.rescan()

    def mark_files(self):
        # ask the user for the file name
        file_filter = self.tr("Data Files (*.apd)")
        val = QtWidgets.QFileDialog.getOpenFileNames(
            self, self.tr("Select Files"), self.base_dir, file_filter)
        files = val[0]

        if len(files) == 0:
            return

        for filename in files:
            logger.info("Marking file {}".format(filename))
            hyperborea.upload.mark_file_for_upload(filename)

        if self.upload_manager:
            self.upload_manager.rescan()

    def next_tab(self):
        new_index = self.tabWidget.currentIndex() + 1
        if new_index >= self.tabWidget.count():
            new_index = 0
        self.tabWidget.setCurrentIndex(new_index)

    def prev_tab(self):
        new_index = self.tabWidget.currentIndex() - 1
        if new_index < 0:
            new_index = self.tabWidget.count() - 1
        self.tabWidget.setCurrentIndex(new_index)

    def collapsed_set(self, collapsed):
        self.collapsed = collapsed
        write_bool_setting(self.settings, "Collapsed", collapsed)
        for tab_widget in self.tab_widgets:
            tab_widget.set_collapsed(collapsed)

    def update_style(self):
        dark_mode = read_bool_setting(self.settings, "DarkMode", True)
        set_style(QtWidgets.QApplication.instance(), dark_mode)

    def current_tab_changed_cb(self, index):
        if index == -1:
            new_tab = None
        else:
            new_tab = self.tab_widgets[index]

        if self.shown_tab == new_tab:
            return  # no change

        if self.shown_tab is not None:
            self.shown_tab.set_is_shown(False)
        if new_tab is not None:
            new_tab.set_is_shown(True)

        self.shown_tab = new_tab
