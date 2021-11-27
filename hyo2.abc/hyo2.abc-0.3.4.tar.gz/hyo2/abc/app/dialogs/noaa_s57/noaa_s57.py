import os
from PySide2 import QtCore, QtGui, QtWidgets

import logging

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.abc.app.app_info import AppInfo
from hyo2.abc.app.dialogs.noaa_s57.noaa_support import NOAASupport
from hyo2.abc.app.qt_progress import QtProgress

logger = logging.getLogger(__name__)


class NOAAS57Dialog(QtWidgets.QDialog):
    media = os.path.join(os.path.dirname(__file__), "media")

    def __init__(self, lib_info: LibInfo, app_info: AppInfo,
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self._li = lib_info
        self._ai = app_info

        fixed_height = 32
        fixed_width = 135

        self.setWindowTitle("NOAA S57 Files")
        self.resize(QtCore.QSize(240, 400))
        self.setMaximumSize(QtCore.QSize(300, 500))

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap(os.path.join(self.media, 'noaa_support.png')))
        hbox.addWidget(logo)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        title = QtWidgets.QLabel()
        my_font = QtGui.QFont()
        my_font.setBold(True)
        title.setFont(my_font)
        title.setText("NOAA Support Files %s" % NOAASupport.support_version)
        hbox.addWidget(title)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        logo = QtWidgets.QLabel()
        logo.setText("""
        These support files are required to visualize<br>
        the .000 outputs in CARIS apps.<br> 
        Execute the 3 steps in order.<br>
        Step #3 requires admin privileges.
        """)
        hbox.addWidget(logo)
        hbox.addStretch()

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button = QtWidgets.QPushButton(self)
        button.setFixedHeight(fixed_height)
        button.setFixedWidth(fixed_width)
        button.setText("#1 -> Unzip archive")
        button.setToolTip('Unzip the internal archive to a local folder')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.noaa_support_unzip)
        hbox.addWidget(button)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button = QtWidgets.QPushButton(self)
        button.setFixedHeight(fixed_height)
        button.setFixedWidth(fixed_width)
        button.setText("#2 -> Copy folder")
        button.setToolTip('Copy the support files to the C:\\CARIS folder')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.noaa_support_copy)
        hbox.addWidget(button)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button = QtWidgets.QPushButton(self)
        button.setFixedHeight(fixed_height)
        button.setFixedWidth(fixed_width)
        button.setText("#3 -> Install files")
        button.setToolTip('Execute the batch file to install the support files (requires admin privileges)')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.noaa_support_install)
        hbox.addWidget(button)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(fixed_height)
        button.setFixedWidth(fixed_height)
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet(
            "QPushButton { background-color: rgba(255, 255, 255, 0); }\n"
            "QPushButton:hover { background-color: rgba(230, 230, 230, 100); }\n"
        )
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)
        hbox.addStretch()

        vbox.addStretch()

    def noaa_support_unzip(self):
        logger.debug("unzipping NOAA Support Files")

        noaa_support = NOAASupport(app_info=self._ai, lib_info=self._li, progress=QtProgress(parent=self))

        if noaa_support.local_noaa_support_folder_present():
            msg = "The support folder was already unzipped:\n" \
                  "- %s\n\n" \
                  "Do you want to force to re-unzip it? If no, go to step #2." \
                  % noaa_support.local_noaa_support_folder()
            # noinspection PyCallByClass,PyArgumentList
            ret = QtWidgets.QMessageBox.information(self, "Unzip folder", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        unzipped = False

        if noaa_support.internal_zip_path_exists():
            internal_zip_path = noaa_support.internal_zip_path()
            logger.debug("internal zip: %s" % internal_zip_path)

            success = noaa_support.unzip_internal_zip()
            logger.debug("installed internal zip: %s" % success)
            if success:
                unzipped = True

        if not unzipped:
            success = noaa_support.download_from_noaa()
            logger.debug("download from noaa: %s" % success)
            if success:
                unzipped = True

        if not unzipped:
            success = noaa_support.download_from_unh()
            logger.debug("download from unh: %s" % success)
            if success:
                unzipped = True

        # noinspection PyArgumentList
        if unzipped and noaa_support.local_noaa_support_folder_present():
            msg = "Success! Go to step #2."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Unzip done!", msg, QtWidgets.QMessageBox.Ok)
            return

        else:
            msg = "Unable to unzip the archive. Do you have a working Internet connection?"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            return

    def noaa_support_copy(self):
        logger.debug("copying NOAA Support Files")

        noaa_support = NOAASupport(app_info=self._ai, lib_info=self._li, progress=QtProgress(parent=self))

        if not noaa_support.local_noaa_support_folder_present():
            msg = "The support folder is not present!\n" \
                  "Did you unzip it? Go to step #1."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Copy folder", msg, QtWidgets.QMessageBox.Ok)
            return

        if noaa_support.system_noaa_support_folder_present():
            msg = "The support folder was already copied:\n" \
                  "- %s\n\n" \
                  "Do you want to force the re-copy? If no, go to step #3." % noaa_support.system_noaa_support_folder()
            # noinspection PyCallByClass,PyArgumentList
            ret = QtWidgets.QMessageBox.information(self, "Copy folder", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return
            noaa_support.delete_system_noaa_support_files()

        copied = noaa_support.copy_local_to_system()
        logger.info(copied)
        if copied and noaa_support.system_noaa_support_folder_present():
            msg = "Success! Go to step #3."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Copy done!", msg, QtWidgets.QMessageBox.Ok)
            return

        else:
            msg = "Unable to copy the folder:\n" \
                  "- %s\n" \
                  "to:\n" \
                  "- %s\n" \
                  "Try to manually do the copy or re-run QC Tools as administrator." \
                  % (noaa_support.local_noaa_support_folder(), noaa_support.caris_root)
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            return

    def noaa_support_install(self):
        logger.debug("installing NOAA Support Files")

        noaa_support = NOAASupport(app_info=self._ai, lib_info=self._li, progress=QtProgress(parent=self))

        msg = "The batch file must be executed as administrator\n" \
              "with all other users logged off the system.\n" \
              "Once executed, follow the instructions in the Windows shell.\n\n" \
              "Do you want to continue with the installation?"
        # noinspection PyCallByClass,PyArgumentList
        ret = QtWidgets.QMessageBox.information(self, "Install files", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.No:
            return

        if not noaa_support.system_noaa_support_folder_present():
            msg = "The support folder is not present!\n" \
                  "Did you copy it? Go to step #2."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Install files", msg, QtWidgets.QMessageBox.Ok)
            return

        if not noaa_support.system_batch_file_exists():
            msg = "The batch file does not exist!\n" \
                  "Did you execute steps #1 and #2? Try to execute them again."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Install files", msg, QtWidgets.QMessageBox.Ok)
            return

        if not Helper.is_user_admin():

            msg = "The app was not executed as admin!\n\n" \
                  "Do you want that this app executes the batch file?\n\n" \
                  "You will be prompted for permissions.\n"

            # noinspection PyCallByClass,PyArgumentList
            ret = QtWidgets.QMessageBox.information(self, "Install files", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:

                msg = "You have then two alternatives:\n" \
                      "#1: Close the app and re-open it using the option \"Run as administrator\"\n" \
                      "or:\n" \
                      "#2: Manually run as administrator the batch file at:\n" \
                      "- %s\n\n" \
                      "For option #2, do you want that the appFMG_8880" \
                      " open the folder with the batch file?" \
                      % (noaa_support.system_batch_file())

                # noinspection PyCallByClass,PyArgumentList
                ret = QtWidgets.QMessageBox.information(self, "Install files", msg,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.Yes:
                    noaa_support.open_system_noaa_support_folder()
                return

            installed = noaa_support.exec_system_batch()
            if installed:
                msg = "Follow the instruction in the windows shell!"
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.information(self, "Windows shell", msg, QtWidgets.QMessageBox.Ok)
                return

            else:
                msg = "Unable to install the support files.\n" \
                      "Try to manually run as administrator the batch file at: %s\n\n" \
                      % (noaa_support.system_batch_file())
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                noaa_support.open_system_noaa_support_folder()
                return

        else:

            installed = noaa_support.exec_system_batch()
            if installed:
                msg = "Success!"
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.information(self, "Installation done!", msg, QtWidgets.QMessageBox.Ok)
                return

            else:
                msg = "Unable to install the support files.\n" \
                      "Try to manually run as administrator the batch file at: %s\n\n" \
                      % (noaa_support.system_batch_file())
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                noaa_support.open_system_noaa_support_folder()
                return

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder(
            "https://www.hydroffice.org/manuals/abc/user_manual_info.html#noaa-s-57-support-files-for-caris"
        )
