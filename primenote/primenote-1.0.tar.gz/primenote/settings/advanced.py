#!/usr/bin/python3
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QSizePolicy, QSpacerItem

try:
    from ..__id__ import APP_NAME, ID
    from ..backend.constants import ConfigDirs, notesDir
    from ..backend.database import AutoComboBoxGlob, AutoFontComboBox, AutoSpinBox
    from ..settings.base import HSpacer, VSpacer, Page
except (ValueError, ImportError):
    from __id__ import APP_NAME, ID
    from backend.constants import ConfigDirs, notesDir
    from backend.database import AutoComboBoxGlob, AutoFontComboBox, AutoSpinBox
    from settings.base import HSpacer, VSpacer, Page


class PageAdvanced(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.repository = Repository(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.repository)
        layout.addWidget(Terminal(self))
        layout.addWidget(Folder(self))
        layout.addItem(VSpacer())


class Terminal(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Terminal", parent)
        colorSchemeBox = AutoComboBoxGlob(parent.db, ("terminal", "color scheme"), "colorscheme", ConfigDirs.TERMINAL)
        fontSizeBox = AutoSpinBox(parent.db, ("terminal", "font size"))
        fontFamilyBox = AutoFontComboBox(parent.db, ("terminal", "font family"))

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QLabel("Colorscheme"), 0, 0, 1, 1)
        layout.addWidget(colorSchemeBox, 0, 1, 1, 2)
        layout.addWidget(QLabel("Font family"), 1, 0, 1, 1)
        layout.addWidget(fontFamilyBox, 1, 1, 1, 2)
        layout.addWidget(QLabel("Font size"), 2, 0, 1, 1)
        layout.addWidget(fontSizeBox, 2, 1, 1, 1)
        layout.addItem(HSpacer(), 2, 2, 1, 1)


class Folder(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Configuration files", parent)
        self.core = parent.core

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        button = QtWidgets.QPushButton(f"Edit {APP_NAME}\nconfiguration")
        button.setSizePolicy(sizePolicy)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.clicked.connect(self._clicked)
        button.setToolTip("Manually edit CSS, QTermWidget\nand Vim configuration files")

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        label = QLabel(f"All changes can be reset to default through the command-line interface, "
                       f"use <b>{ID} -h</b> for more informations.")
        label.setSizePolicy(sizePolicy)
        label.setWordWrap(True)

        spacer = QSpacerItem(5, 0, QSizePolicy.Fixed, QSizePolicy.Maximum)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)
        layout.addItem(spacer)
        layout.addWidget(button)

    def _clicked(self):
        self.core.fileManager(ConfigDirs.CFG / "ui")


class Repository(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Notes repository", parent)
        self.core = parent.core

        label = QLabel("Set a new location for the notes folder (restart required)")
        button = QtWidgets.QPushButton("Browse")
        button.clicked.connect(self._clicked)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText(str(notesDir()))

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(self.lineEdit, 1, 0, 1, 1)
        layout.addWidget(button, 1, 1, 1, 1)

    @property
    def path(self) -> Path:
        path = Path(self.lineEdit.text())
        if path.is_dir():
            return path
        return ConfigDirs.NOTES

    def _clicked(self):
        dialog = QtWidgets.QFileDialog(self, "Select a notes repository", str(ConfigDirs.NOTES), "")
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            self.lineEdit.setText(path)
