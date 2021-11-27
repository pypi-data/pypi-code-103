from PySide2 import QtCore, QtGui, QtWidgets

import logging

from hyo2.abc.lib.lib_info import LibInfo
from hyo2.abc.app.app_info import AppInfo
from hyo2.abc.app.dialogs.about.tabs.general_info import GeneralInfoTab
from hyo2.abc.app.dialogs.about.tabs.license import LicenseTab
from hyo2.abc.app.dialogs.about.tabs.local_environment import LocalEnvironmentTab
from hyo2.abc.app.dialogs.about.tabs.gdal_info import GdalInfoTab

logger = logging.getLogger(__name__)


class AboutDialog(QtWidgets.QDialog):

    def __init__(self, lib_info: LibInfo, app_info: AppInfo,
                 with_locale_tab: bool = False, with_gdal_tab: bool = False, with_ocs_email: bool = False,
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self._li = lib_info
        self._ai = app_info

        self.with_locale_tab = with_locale_tab
        self.with_gdal_tab = with_gdal_tab

        self.setObjectName("AboutDialog")
        self.setWindowTitle("About")
        self.setMinimumSize(400, 200)
        self.resize(620, 350)

        top_layout = QtWidgets.QHBoxLayout()
        self.setLayout(top_layout)

        # left layout

        left_widget = QtWidgets.QWidget()
        left_widget.setMaximumWidth(180)
        top_layout.addWidget(left_widget)
        left_layout = QtWidgets.QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_layout.addStretch()
        logo_layout = QtWidgets.QHBoxLayout()
        left_layout.addLayout(logo_layout)
        logo_layout.addStretch()
        self.logo = QtWidgets.QLabel()
        self.logo.setPixmap(QtGui.QPixmap(self._ai.app_icon_path).scaled(90, 90, QtCore.Qt.KeepAspectRatio))
        self.logo.resize(90, 90)
        # self.logo.setScaledContents(False)
        logo_layout.addWidget(self.logo)
        logo_layout.addStretch()
        self.name = QtWidgets.QLabel("%s v.%s" % (app_info.app_name, app_info.app_version))
        self.name.setObjectName("AboutName")
        self.name.resize(100, 100)
        self.name.setAlignment(QtCore.Qt.AlignCenter)
        self.name.setWordWrap(True)
        left_layout.addWidget(self.name)
        left_layout.addStretch()

        # right layout

        right_layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(right_layout)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.South)
        self.general_info_tab = GeneralInfoTab(lib_info=self._li, parent=self, with_ocs_email=with_ocs_email)
        self.tab_widget.addTab(self.general_info_tab, "Overview")
        self.license_tab = LicenseTab(app_info=self._ai, parent=self)
        self.tab_widget.addTab(self.license_tab, "License")
        if self.with_locale_tab:
            self.local_environment_tab = LocalEnvironmentTab(self)
            self.tab_widget.addTab(self.local_environment_tab, "Local")
        if self.with_gdal_tab:
            self.gdal_tab = GdalInfoTab(self)
            self.tab_widget.addTab(self.gdal_tab, "GDAL")
        self.tab_widget.setCurrentIndex(0)
        right_layout.addWidget(self.tab_widget)

    def switch_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
