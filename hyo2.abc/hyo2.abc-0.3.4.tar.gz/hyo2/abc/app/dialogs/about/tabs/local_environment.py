from collections import OrderedDict
import locale
import logging
import platform
import sys
from PySide2 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)


class LocalEnvironmentTab(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setObjectName("LocalEnvironmentTable")
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        info = self._collect_info()
        self.table.setRowCount(len(info))
        for idx, key in enumerate(info.keys()):
            self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(key))
            self.table.setItem(idx, 1, QtWidgets.QTableWidgetItem(info[key]))
        self.table.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.layout.addWidget(self.table)

    @classmethod
    def _collect_info(cls) -> OrderedDict:
        info = OrderedDict()

        info["Architecture"] = " ".join(platform.architecture())
        info["Machine/Processor"] = "%s %s" % (platform.machine(), platform.processor())
        info["Network Name"] = "%s" % (platform.node(),)
        info["Platform"] = "%s" % (platform.platform(),)
        info["Python"] = "%s %s" % (platform.python_implementation(), platform.python_version())
        info["System/OS"] = "%s" % (platform.system(),)

        # noinspection PyBroadException
        try:
            import psutil
            info["Physical Memory"] = "%.1f MB" % (psutil.virtual_memory().total / 1024 / 1024,)
            for partition in psutil.disk_partitions():
                info["HD %s" % partition.mountpoint] = \
                     "%.1f GB" % (psutil.disk_usage(partition.mountpoint).total / 1024 / 1024 / 1024,)

        except BaseException:
            pass

        info["Locale"] = "%s" % (locale.getlocale(),)
        info["Default Encoding"] = "%s" % sys.getdefaultencoding()
        info["Filesystem Encoding"] = "%s" % sys.getfilesystemencoding()

        # noinspection PyBroadException
        try:
            qt_locale = QtCore.QLocale()
            info["Qt Local"] = qt_locale.name()
            info["Qt System Local"] = qt_locale.system().name()
            info["Qt Language"] = qt_locale.languageToString(qt_locale.language())
            info["Qt Decimal Point"] = qt_locale.decimalPoint()
            # noinspection PyArgumentList
            info["Qt image formats"] = ", ".join(
                [str(fmt) for fmt in QtGui.QImageReader.supportedImageFormats()])

        except BaseException:
            pass

        return info
