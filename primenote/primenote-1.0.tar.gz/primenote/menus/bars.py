#!/usr/bin/python3
from PyQt5 import QtWidgets, QtCore
try:
    from ..backend import logger
    from ..backend.constants import ConfigDirs
except (ValueError, ImportError):
    from backend import logger
    from backend.constants import ConfigDirs

log = logger.new(__name__)


# # # # # TITLE BAR # # # # #

class MouseFilter(QtCore.QObject):
    def __init__(self, note):
        super().__init__()
        self.note = note
        self.core = note.core
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setToolTipDuration(0)
        self.debounce = 0

    def mouseDoubleClickEvent(self, event):
        """ Handler for double click event """
        self.core.execute(self.group, "doubleclick", self.note.path)

    def mousePressEvent(self, event):
        """ Handler for mouse button events """
        buttons = {
            QtCore.Qt.LeftButton: "left",
            QtCore.Qt.MiddleButton: "middle",
            QtCore.Qt.RightButton: "right",
        }
        button = buttons.get(event.button())
        self.core.execute(self.group, button, self.note.path)
        self.note.mousePressEvent(event)

    def wheelEvent(self, event):
        """ Handler for mouse wheel events """
        threshold = self.core.sdb["general"]["wheel threshold"]
        if self.debounce >= threshold:
            direction = "up" if event.angleDelta().y() > 0 else "down"
            self.core.execute(self.group, direction, self.note.path)
        self.debounce += 1 if self.debounce < threshold else -threshold


class TitleCloseButton(QtWidgets.QPushButton, MouseFilter):
    group = "close"

    def __init__(self, note):
        super().__init__(note)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.setObjectName("topbar-close")
        self.setText("×")


class TitleLabel(QtWidgets.QLabel, MouseFilter):
    group = "title"

    def __init__(self, note):
        super().__init__(note)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        self.setObjectName("topbar-title")


class TitleStatusButton(QtWidgets.QPushButton, MouseFilter):
    group = "status"

    def __init__(self, note):
        super().__init__(note)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.setObjectName("topbar-status")


# # # # # MESSAGE BAR # # # # #

class MessageLabel(QtWidgets.QLabel):
    def __init__(self, note):
        super().__init__()
        self.note = note
        self.core = note.core
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)

    def autoWrap(self):
        """ Disables word wrap when the message bar horizontal space is sufficient """
        self.setWordWrap(self.isBarFull)

    @property
    def enabled(self) -> bool:
        """ Determines if the message bar should be shown or hidden """
        msgbar = self.note.msgbarFrame
        items = sum(1 for _ in msgbar.findChildren(QtWidgets.QLabel))
        folderEnabled = self.core.sdb["message bar"]["folder"]
        folderLess = self.note.path.parent == ConfigDirs.NOTES
        if folderEnabled and folderLess:
            items -= 1
        return items > 0

    @property
    def isBarFull(self) -> bool:
        """ Measures the available horizontal space based on the real width of unwrapped
            labels. This include the space used by CSS padding, margins and font metrics """
        used = 0
        msgbar = self.note.msgbarFrame
        for label in msgbar.findChildren(QtWidgets.QLabel):
            mock = QtWidgets.QLabel(label.text())
            mock.setObjectName(label.objectName())
            mock.adjustSize()
            used += mock.width()
        margins = self.note.contentsMargins()
        available = self.note.width() - margins.left() - margins.right()
        return (available - used) <= 1

    def update(self):
        """ Wrapper for private _update() function. Prevents windows resizing by enabling wordwrap
            before setText() call. Toggles message bar visibility as needed """
        if self.enabled:
            self.setWordWrap(True)
            self._update()
            self.autoWrap()
        try:
            if self.body.isVisible():
                self.note.msgbarFrame.setVisible(self.enabled)
        except AttributeError:  # body not yet created
            pass


class FolderLabel(MessageLabel):
    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self.setObjectName("msgbar-folder")

    def _update(self):
        """ Updates the folder label according to the current note path """
        path = self.note.path.relative_to(ConfigDirs.NOTES)
        path = str(path.parent)
        path = "" if path == "." else path
        self.setText(path)


# # # # # TOOL BAR # # # # #

class ToolbarSpacer(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        policy = QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored
        self.setSizePolicy(*policy)
        self.setObjectName("toolbar-spacer")
        self.hide()


class ToolButton(QtWidgets.QPushButton):
    def __init__(self, note, action):
        super().__init__()
        self.note = note
        self.action = note.actions[action]
        self.setObjectName("toolbar-icon")
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setToolTip(self.action.label)
        self.clicked.connect(self._clicked)

    def _clicked(self, event):
        """ Handler for left click event """
        log.info(f"{self.note.id} : {self.action.label}")
        try:
            self.action.call()
        except TypeError:
            self.action.call(self.note.path)


# # # # # HOT BAR # # # # #

class HotbarSpacer(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        policy = QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored
        self.setSizePolicy(*policy)
        self.setObjectName("hotbar-spacer")


class SizeGrip(QtWidgets.QSizeGrip):
    def __init__(self, note, tag=None):
        super().__init__(note)
        self.note = note
        self.setObjectName(tag)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)


class SizeGripVertical(SizeGrip):
    def __init__(self, note):
        super().__init__(note)
        self.setObjectName("center")

    def mousePressEvent(self, event):
        """ Blocks horizontal resizing """
        self.note.setFixedWidth(self.note.width())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Restores horizontal resizing """
        self.note.setFixedWidth(QtWidgets.QWIDGETSIZE_MAX)
        super().mouseReleaseEvent(event)
