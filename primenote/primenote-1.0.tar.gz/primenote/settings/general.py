#!/usr/bin/python3
from PyQt5 import QtCore, QtGui, QtWidgets

try:
    from ..backend.database import AutoCheckBox
    from ..settings.base import HSpacer, VSpacer, Page
except (ValueError, ImportError):
    from backend.database import AutoCheckBox
    from settings.base import HSpacer, VSpacer, Page


class PageGeneral(Page):
    def __init__(self, *args):
        super().__init__(*args)
        self.icons = Icons(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(General(self))
        layout.addItem(HSpacer())
        layout.addWidget(MessageBar(self))
        layout.addItem(HSpacer())
        layout.addWidget(Launcher(self))
        layout.addItem(HSpacer())
        layout.addWidget(self.icons)
        layout.addItem(VSpacer())


class General(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("General", parent)
        hotkeysBox = AutoCheckBox("Enable hotkeys", parent.db, ("general", "hotkeys"))
        minBox = AutoCheckBox("Minimize pinned notes on startup", parent.db, ("general", "minimize"))
        skipBox = AutoCheckBox("Skip taskbar", parent.db, ("general", "skip taskbar"))
        repositionBox = AutoCheckBox("Move to center if out of sight", parent.db, ("general", "reposition"))
        copyBox = AutoCheckBox("Enable rich text internal copy/paste", parent.db, ("general", "accept qrichtext"))

        skipBox.setToolTip("Hide the visible notes from system taskbar")
        repositionBox.setToolTip("On screen change, reposition out of\nbound notes to the screen center")
        copyBox.setToolTip("Preserve formatting when copy/pasting\ninto the Rich Text mode")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(hotkeysBox)
        layout.addWidget(minBox)
        layout.addWidget(skipBox)
        layout.addWidget(repositionBox)
        layout.addWidget(copyBox)


class MessageBar(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Message bar", parent)
        folderBox = AutoCheckBox("Current folder", parent.db, ("message bar", "folder"))
        wordBox = AutoCheckBox("Word count", parent.db, ("message bar", "words"))
        pixelBox = AutoCheckBox("Pixel count", parent.db, ("message bar", "pixels"))

        folderBox.setToolTip("Display the current folder and subfolders, if any")
        wordBox.setToolTip("Show a word and characters counter (text mode)")
        pixelBox.setToolTip("Show the size in pixels (image mode)")
        self.setToolTip("The message bar display basic information at the note bottom")

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(folderBox)
        layout.addWidget(wordBox)
        layout.addWidget(pixelBox)


class Launcher(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Launcher", parent)
        caseBox = AutoCheckBox("Case sensitive", parent.db, ("launcher", "case"))
        hideBox = AutoCheckBox("Hide on launch", parent.db, ("launcher", "hide"))

        hideBox.setToolTip("Close the dialog once a note is chosen")
        self.setToolTip("The launcher is a standalone dialog which allow to quickly search\n"
                        "among the note repository. It is accessible through command line\n"
                        "interface or 'Search repository' core action")

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(caseBox)
        layout.addWidget(hideBox)


class Icons(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Context menus icons color", parent)
        self.parent = parent
        self.color = self.currentColor()
        darkButton = QtWidgets.QPushButton("Dark")
        lightButton = QtWidgets.QPushButton("Light")
        customButton = QtWidgets.QPushButton("Custom")

        darkButton.setToolTip("Dark icon color for light themes")
        lightButton.setToolTip("Light icon color for dark themes")
        customButton.setToolTip("Choose a custom icon color")
        self.setToolTip("These shortcut allow to quickly change the icon color\nof all context menus.")

        icon = parent.core.icons["toggle"]
        icons = {darkButton: "#404040", lightButton: "#8f8f8f", customButton: "#d4af37"}
        for button, color in icons.items():
            color = QtGui.QColor(color)
            icon = parent.core.colorize(icon, color)
            button.setIcon(icon)
            button.setFocusPolicy(QtCore.Qt.NoFocus)
            button.clicked.connect(self.setMenuIconsColor)
            button.color = color if button != customButton else None

        layout = QtWidgets.QHBoxLayout(self)
        layout.addItem(HSpacer())
        layout.addWidget(darkButton)
        layout.addWidget(lightButton)
        layout.addWidget(customButton)
        layout.addItem(HSpacer())

    def colorInputDialog(self) -> QtGui.QColor:
        """ Opens a color picker dialog """
        color = QtWidgets.QColorDialog.getColor(initial=self.color, title="Pick a color for menu icons")
        return color if color.isValid() else self.color

    def currentColor(self) -> QtGui.QColor:
        """ Returns the current menu icon color fetched from CSS files """
        css = self.parent.core.getNoteDecorationsCSS()
        return QtGui.QColor(css["menu-icon"])

    def setMenuIconsColor(self):
        """ Schedules the choosen color to be applied once the parent dialog is accepted """
        color = QtCore.QObject.sender(self).color
        color = color if color else self.colorInputDialog()
        self.color = color
