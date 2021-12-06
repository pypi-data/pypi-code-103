#!/usr/bin/python3
import json
from copy import deepcopy
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDialogButtonBox as QButtonBox

try:
    from ..__id__ import APP_NAME
    from ..backend import logger
    from ..backend.constants import ConfigDirs, ConfigFiles
    from ..settings.general import PageGeneral
    from ..settings.profile import PageProfile
    from ..settings.mouse import PageMouse
    from ..settings.hotkeys import PageHotkeys
    from ..settings.menus import PageCoreMenu, PageNoteContextMenu, PageNoteToolbarMenu
    from ..settings.logs import PageLogs
    from ..settings.advanced import PageAdvanced
    from ..settings.reset import ResetDialog
except (ValueError, ImportError):
    from __id__ import APP_NAME
    from backend import logger
    from backend.constants import ConfigDirs, ConfigFiles
    from settings.general import PageGeneral
    from settings.profile import PageProfile
    from settings.mouse import PageMouse
    from settings.hotkeys import PageHotkeys
    from settings.menus import PageCoreMenu, PageNoteContextMenu, PageNoteToolbarMenu
    from settings.logs import PageLogs
    from settings.advanced import PageAdvanced
    from settings.reset import ResetDialog

log = logger.new(__name__)


class Settings(QtWidgets.QDialog):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setWindowIcon(core.icons["tray"])
        self.resize(550, 1)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        self.sideMenu = QtWidgets.QListWidget()
        self.sideMenu.setSizePolicy(sizePolicy)
        self.sideMenu.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.sideMenu.addItems(["General", "Profile default", "Mouse events", "Hotkeys", "Core menus",
                                "Note context menus", "Note toolbars menus", "Logs and archives", "Advanced"])
        self.sideMenu.item(0).setSelected(True)
        self.sideMenu.selectionModel().selectionChanged.connect(self.setPageIndex)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(5)
        self.dbCopy = deepcopy(dict(core.sdb))
        self.general = PageGeneral(core, self.dbCopy)
        self.advanced = PageAdvanced(core, self.dbCopy)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setSizePolicy(sizePolicy)
        self.stack.addWidget(self.general)
        self.stack.addWidget(PageProfile(core, self.dbCopy))
        self.stack.addWidget(PageMouse(core, self.dbCopy))
        self.stack.addWidget(PageHotkeys(core, self.dbCopy))
        self.stack.addWidget(PageCoreMenu(core, self.dbCopy))
        self.stack.addWidget(PageNoteContextMenu(core, self.dbCopy))
        self.stack.addWidget(PageNoteToolbarMenu(core, self.dbCopy))
        self.stack.addWidget(PageLogs(core, self.dbCopy))
        self.stack.addWidget(self.advanced)

        frame = self.BottomFrame(self)
        topLayout = QtWidgets.QGridLayout()
        topLayout.addWidget(self.sideMenu, 0, 0, 1, 2)
        topLayout.addWidget(self.stack, 0, 2, 1, 1)
        layout = QtWidgets.QGridLayout(self)
        layout.addLayout(topLayout, 0, 0, 1, 1)
        layout.addWidget(frame, 1, 0, 1, 1)
        self.show()

    def accept(self):
        super().accept()
        self.apply()

    def apply(self):
        """ Applies new application settings """
        newColor = self.general.icons.color.name()
        oldColor = self.general.icons.currentColor().name()
        if newColor != oldColor:
            self.core.setMenuIconsColor(newColor)

        newNotesPath = self.advanced.repository.path
        if newNotesPath == ConfigDirs.CFG / "notes":
            self._discardPathFile()
        else:
            self._setNotesPath(newNotesPath)

        self.core.sdb.update(self.dbCopy)
        log.info("New settings applied")

    def reset(self):
        """ Handles restore to default dialog """
        dialog = ResetDialog(self.core)
        if dialog.exec() and dialog.isChecked():
            self.accept()
            for key, item in dialog.checkboxes.items():
                if item.isChecked():
                    dialog.resetKey(key)

            if dialog.checkboxes["terminal"].isChecked():  # Reset 'Advanced' tab
                self._discardPathFile()
            self.core.settings()

    def setPageIndex(self):
        """ Updates the stack widget according to side menu changes """
        index = self.sideMenu.currentRow()
        self.stack.setCurrentIndex(index)

    def _discardPathFile(self):
        """ Silently deletes a file """
        try:
            ConfigFiles.PATHS.unlink()
        except (FileNotFoundError, PermissionError):
            pass

    def _setNotesPath(self, path: Path):
        """ Changes note repository location in paths.json """
        try:
            with open(ConfigFiles.PATHS, encoding="utf-8") as f:
                paths = json.load(f)
        except FileNotFoundError:
            paths = {}

        paths["notes"] = str(path)
        with open(ConfigFiles.PATHS, "w", encoding="utf-8") as f:
            f.write(json.dumps(paths, indent=2))

    class BottomFrame(QtWidgets.QFrame):
        def __init__(self, parent):
            super().__init__()
            self.parent = parent
            self.setFrameShape(self.NoFrame)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(1)

            buttons = QButtonBox.Cancel | QButtonBox.Ok | QButtonBox.Apply | QButtonBox.RestoreDefaults
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(2)
            self.buttonBox = QButtonBox()
            self.buttonBox.setSizePolicy(sizePolicy)
            self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
            self.buttonBox.setStandardButtons(buttons)
            self.buttonBox.accepted.connect(parent.accept)
            self.buttonBox.rejected.connect(parent.reject)
            self.buttonBox.clicked.connect(self._clicked)

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.buttonBox)

        def _clicked(self, button: QtWidgets.QPushButton):
            """ Parses clicked button type """
            button = self.buttonBox.standardButton(button)
            if button == QButtonBox.Apply:
                self.parent.apply()
            elif button == QButtonBox.RestoreDefaults:
                self.parent.reset()
