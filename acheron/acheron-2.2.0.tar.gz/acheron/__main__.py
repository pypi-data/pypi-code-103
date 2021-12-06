#!/usr/bin/env python3
import setproctitle  # NOTE: this should be first!

import logging.handlers
import multiprocessing
import os
import sys
import time

from PySide2 import QtCore, QtGui, QtWidgets

import acheron
import asphodel
import hyperborea.proxy

from .plotmain import PlotMainWindow
from . import acheron_rc  # needed for the icon

logger = logging.getLogger(__name__)


def main_is_frozen():
    """Return True if the script is frozen, False otherwise."""
    return getattr(sys, 'frozen', False)


def setup_logging():
    """Configure logging for the whole program."""

    def my_excepthook(exctype, value, traceback):
        """Log the caught exception using the logging module."""
        exc_info = (exctype, value, traceback)
        logger.error("Uncaught Exception", exc_info=exc_info)

    sys.excepthook = my_excepthook

    # get an appropriate location for the log file
    logdir = QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.DataLocation)
    logfile = os.path.join(logdir, "main.log")

    # make sure the directory exists
    os.makedirs(logdir, exist_ok=True)

    # filter for creating %(optdevice) format option
    optdevice_filter = hyperborea.proxy.OptionalDeviceStringFilter("[%s] ", "")

    # create a log file handler
    file_log_handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=10e6, backupCount=1, encoding='utf-8')
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(optdevice)s%(message)s")
    file_formatter.default_time_format = '%Y-%m-%dT%H:%M:%S'
    file_formatter.default_msec_format = '%s,%03dZ'
    file_formatter.converter = time.gmtime
    file_log_handler.addFilter(optdevice_filter)
    file_log_handler.setFormatter(file_formatter)
    file_log_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_log_handler)
    root_logger.setLevel(logging.DEBUG)

    # remove pyusb's logging info
    pyusb_logger = logging.getLogger("usb")
    pyusb_logger.propagate = False

    # suppress boto3 (aws) debug messages
    logging.getLogger('boto3').setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('s3transfer').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)


def create_empty_settings():
    settings = QtCore.QSettings()

    setting_keys = [
        "UpdateTimerInterval",
        "GraphTimerInterval",
        "StreamTimeout",
        "FirmwareRootDir",
        "DiskCachePath",
        "RFTest",
    ]

    for setting_key in setting_keys:
        value = settings.value(setting_key)
        if not value:
            settings.setValue(setting_key, "")


def force_exit():
    # based on pyqtgraph.exit, with fix for macos

    # # invoke atexit callbacks
    import atexit
    atexit._run_exitfuncs()

    # # close file handles
    if sys.platform == 'darwin':
        # trying to close 7 produces an illegal instruction on the Mac
        os.closerange(3, 7)
        os.closerange(8, 4096)
    else:
        os.closerange(3, 4096)  # just guessing on the maximum descriptor count

    os._exit(0)


def main():
    """Run the program."""

    # freeze_support() MUST be first. Anything before this will cease to exist
    multiprocessing.freeze_support()

    # spawn is only option on windows, linux needs spawn or forkserver to work
    multiprocessing.set_start_method("spawn")

    setproctitle.setproctitle("acheron")

    # work around for botocore data
    if main_is_frozen():
        cacert = os.path.join(os.path.dirname(sys.executable), 'botodata',
                              'cacert.pem')
        os.environ["AWS_CA_BUNDLE"] = cacert
        botodata = os.path.join(os.path.dirname(sys.executable), 'botodata')
        os.environ["AWS_DATA_PATH"] = botodata

    if not sys.stdout or not sys.stderr:
        sys.stdout = open(os.devnull)
        sys.stderr = open(os.devnull)

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Acheron")
    app.setOrganizationDomain("suprocktech.com")
    app.setOrganizationName("Suprock Tech")

    QtGui.QIcon.setThemeName("suprock")

    # load the application icon
    icon = QtGui.QIcon()
    icon_reader = QtGui.QImageReader(":/acheron.ico")
    while True:
        pixmap = QtGui.QPixmap.fromImage(icon_reader.read())
        icon.addPixmap(pixmap)
        if not icon_reader.jumpToNextImage():
            break
    app.setWindowIcon(icon)

    # remove "What's This" button across the whole application
    app.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)

    # force the settings to use an INI file instead of the registry
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)

    app.setApplicationVersion(acheron.__version__)

    # add selectable text to all message boxes
    app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

    setup_logging()
    create_empty_settings()

    logger.info("Acheron started (Version {})".format(acheron.__version__))

    try:
        missing_funcs = asphodel.nativelib.missing_funcs
    except AttributeError:
        missing_funcs = []  # to bypass the next warning
        message = "Asphodel python mismatch!"
        logging.warning(message)
        QtWidgets.QMessageBox.warning(None, "Warning", message)

    if missing_funcs:
        missing_str = ", ".join(sorted(missing_funcs))
        logging.warning("Missing Asphodel functions: {}".format(missing_str))
        QtWidgets.QMessageBox.warning(None, "Warning",
                                      "Asphodel library mismatch!")

    proxy_manager = hyperborea.proxy.DeviceProxyManager("acheron-device")

    mainwin = PlotMainWindow(proxy_manager)
    mainwin.show()
    app.exec_()

    logger.info("Acheron main window closed")

    proxy_manager.stop()
    if mainwin.upload_manager:
        mainwin.upload_manager.stop()
        mainwin.upload_manager.join()

    logger.info("Acheron finished")

    force_exit()


if __name__ == '__main__':
    main()
