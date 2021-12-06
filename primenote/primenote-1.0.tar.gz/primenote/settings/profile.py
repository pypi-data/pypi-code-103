#!/usr/bin/python3
import sys
from typing import Tuple
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QSizePolicy

try:
    from ..backend.constants import ConfigDirs
    from ..backend.database import (AbstractDatabaseInterface, AutoCheckBox, AutoComboBoxGlob,
                                    AutoDoubleSpinBox, AutoLineEdit, AutoSpinBox)
    from ..settings.base import HSpacer, VSpacer, Page, MODE_TO_KEY, KEY_TO_MODE
except (ValueError, ImportError):
    from backend.constants import ConfigDirs
    from backend.database import (AbstractDatabaseInterface, AutoCheckBox, AutoComboBoxGlob,
                                  AutoDoubleSpinBox, AutoLineEdit, AutoSpinBox)
    from settings.base import HSpacer, VSpacer, Page, MODE_TO_KEY, KEY_TO_MODE


class PageProfile(Page):
    def __init__(self, *args):
        super().__init__(*args)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(Profile(self))
        layout.addItem(VSpacer())


class Profile(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Default profile", parent)
        styleBox = AutoComboBoxGlob(parent.db, ("profile default", "style"), "css", ConfigDirs.STYLES)
        paletteBox = AutoComboBoxGlob(parent.db, ("profile default", "palette"), "css", ConfigDirs.PALETTES)
        nameBox = AutoLineEdit(parent.db, ("general", "default name"))

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        modeBox = ModeComboBox(parent.db, ("profile default", "mode"))
        opacityBox = AutoDoubleSpinBox(parent.db, ("profile default", "opacity"))
        wrapBox = AutoCheckBox("Word wrap", parent.db, ("profile default", "wrap"))
        pinBox = AutoCheckBox("Pinned", parent.db, ("profile default", "pin"))
        widthBox = AutoSpinBox(parent.db, ("profile default", "width"))
        widthBox.setSizePolicy(sizePolicy)
        widthBox.setSingleStep(10)
        heightBox = AutoSpinBox(parent.db, ("profile default", "height"))
        heightBox.setSizePolicy(sizePolicy)
        heightBox.setSingleStep(10)

        self.setToolTip("Define the default options used for all\nnewly loaded notes")
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QLabel("Size (w:h)"), 0, 0, 1, 1)
        layout.addWidget(widthBox, 0, 2, 1, 1)
        layout.addWidget(QLabel(":"), 0, 3, 1, 1)
        layout.addWidget(heightBox, 0, 4, 1, 1)
        layout.addItem(HSpacer(), 0, 5, 1, 1)
        layout.addWidget(QLabel("Opacity"), 1, 0, 1, 1)
        layout.addWidget(opacityBox, 1, 2, 1, 1)
        layout.addWidget(QLabel("Name"), 2, 0, 1, 1)
        layout.addWidget(nameBox, 2, 2, 1, 4)
        layout.addWidget(QLabel("Palette"), 3, 0, 1, 1)
        layout.addWidget(paletteBox, 3, 2, 1, 4)
        layout.addWidget(QLabel("Style"), 4, 0, 1, 1)
        layout.addWidget(styleBox, 4, 2, 1, 4)
        layout.addWidget(QLabel("Mode"), 5, 0, 1, 1)
        layout.addWidget(modeBox, 5, 2, 1, 4)
        layout.addWidget(wrapBox, 6, 0, 1, 1)
        layout.addWidget(pinBox, 7, 0, 1, 1)


class ModeComboBox(AbstractDatabaseInterface, QtWidgets.QComboBox):
    def __init__(self, db: dict, slices: Tuple):
        super(QtWidgets.QComboBox, self).__init__()
        AbstractDatabaseInterface.__init__(self, db, slices)
        modes = ["Plain text", "Rich text"]
        if "QTermWidget" in sys.modules:
            modes += ["Console", "Vim"]

        self.addItems(sorted(modes))
        self.load()
        self.currentTextChanged.connect(self._save)

    def load(self):
        """ Sets the default profile value as the current text """
        mode = KEY_TO_MODE[self._load()]
        self.setCurrentText(mode)

    def value(self) -> str:
        """ Translates the displayed mode label into its database key """
        mode = MODE_TO_KEY[self.currentText()]
        return mode
