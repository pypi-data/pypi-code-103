#!/usr/bin/python3
import ctypes
import shutil
import sys
from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Callable, Iterable, Tuple
from PyQt5 import QtWidgets, QtCore, QtGui

try:
    from ..backend import logger
    from ..backend.constants import ConfigDirs, RootFiles, Tuples
    from ..menus.note import ModeMenu, PaletteMenu, StyleMenu, ToolMenu
    from ..menus.bars import (FolderLabel, HotbarSpacer, SizeGrip, SizeGripVertical, TitleCloseButton,
                              TitleLabel, TitleStatusButton, ToolbarSpacer, ToolButton)
except (ValueError, ImportError):
    from backend import logger
    from backend.constants import ConfigDirs, RootFiles, Tuples
    from menus.note import ModeMenu, PaletteMenu, StyleMenu, ToolMenu
    from menus.bars import (FolderLabel, HotbarSpacer, SizeGrip, SizeGripVertical, TitleCloseButton,
                            TitleLabel, TitleStatusButton, ToolbarSpacer, ToolButton)

log = logger.new(__name__)


class NoteWindow(QtWidgets.QWidget):
    shown = QtCore.pyqtSignal(Path)
    hidden = QtCore.pyqtSignal(Path)

    def __init__(self, core, path: Path):
        super().__init__()
        self.core = core
        self.setWindowTitle(path.stem)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setContentsMargins(1, 0, 1, 1)
        self.setAcceptDrops(True)
        self.movable = False
        self.keyFilter = KeyFilter(self)
        self.syncTimer = QtCore.QTimer(interval=1000)
        self.syncTimer.timeout.connect(self._sync)
        self.syncTimer.start()

    def closeEvent(self, event):
        """ Schedules Note object for deletion, remove if blank """
        log.info(f"Closing '{self.id}'")
        if "save" in dir(self):
            self.save()

        self.deleteLater()
        self._blank()
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        """ Allows the implementation of a customized dropEvent handler """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        """ Transferts dropped URLs to the global DropFilter thread """
        for url in event.mimeData().urls():
            url = url.toString(QtCore.QUrl.PreferLocalFile)
            QtCore.QMetaObject.invokeMethod(self.core.dropFilter, "filter", QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG(object, self.path),  # Path of sender
                                            QtCore.Q_ARG(str, url))  # URL to filter
        super().dropEvent(event)

    def focusInEvent(self, event):
        self.shown.emit(self.path)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """ Saves geometry on focus out event """
        if self.id in self.core.pdb:
            self.saveGeometry()
        super().focusOutEvent(event)

    def hideEvent(self, event):
        self.hidden.emit(self.path)
        super().hideEvent(event)

    def keyPressEvent(self, event):
        """ Hotkeys handler """
        self.keyFilter.update(event)
        isValid = self.mode not in ("plain", "html")  # KeyEvents are also handled into Q_TextEdit()
        if self.keyFilter.match() and isValid:
            self.keyFilter.execute()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """ Hotkeys handler """
        self.keyFilter.update(event)

    def mouseMoveEvent(self, event):
        """ Enables window mouse dragging """
        if self.movable:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(event.globalPos() - self.dragPosition)

    def mousePressEvent(self, event):
        """ Enables window mouse dragging """
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            self.movable = True

    def mouseReleaseEvent(self, event):
        """ Prevents mouse dragging on sub-widgets """
        self.movable = False

    @property
    def onScreen(self) -> bool:
        """ Verifies if the window fits inside of screen boundaries """
        frame = self.frameGeometry()
        topLeft = frame.topLeft()
        bottomRight = frame.bottomRight()
        for screen in self.core.screens():
            if screen.contains(topLeft) and screen.contains(bottomRight):
                return True
        return False

    def paintEvent(self, event):
        """ Draws a one pixel black border around window """
        border = QtGui.QColor("black")
        background = self.palette().color(QtGui.QPalette.Background)
        background = QtGui.QColor(background)
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(border))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setBrush(QtGui.QBrush(background))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

    def resizeEvent(self, event):
        for label in self.msgbarFrame.findChildren(QtWidgets.QLabel):
            label.autoWrap()
            if self.mode == "image":
                label.update()
        super().resizeEvent(event)

    def showEvent(self, event):
        """ Shows a note, hides it from system taskbar and updates its style and geometry """
        log.info(f"{self.id} : Show event")
        if not self.path.is_file(): return
        skip = self.core.sdb["general"]["skip taskbar"]
        if skip and sys.platform.startswith("linux"):
            self.xprop.start()
            self.xprop.waitForFinished()
        self.showNormal()  # Fix "ghost note" glitch when hidden from another desktop
        self.restoreGeometry()
        self.decorate()
        self.unroll()
        self.activateWindow()

        reposition = self.core.sdb["general"]["reposition"]
        if reposition and not self.onScreen:
            self.resetPosition()

    def _sync(self):
        """ Unloads externally deleted files """
        if not self.path.is_file():
            log.warning(f"{self.id} : Deleted by an external process")
            self.close()
            self.core.setup.lint()


class Note(NoteWindow):
    def __init__(self, core, path: Path):
        super().__init__(core, path)
        self.path = path

    def decorate(self):
        """ Applies profile's stylesheet and NoteDecorations{} selector attributes """
        self.setup.css()
        self.setup.icons()
        self.setup.actions()
        self.setup.toolbar()
        self.setup.status()

    def duplicate(self):
        """ Clones the current note """
        folders = self.path.parent.relative_to(ConfigDirs.NOTES)
        new = self.core.nameIndex(ConfigDirs.NOTES / folders / self.path.name)
        shutil.copy(self.path, new)

        # Update the profile and load the clone
        x, y = self.pos().x(), self.pos().y()
        w, h = self.width(), self.height()
        nid = str(new.relative_to(ConfigDirs.NOTES))
        self.core.pdb[nid] = deepcopy(self.core.pdb[self.id])
        self.core.pdb[nid]["position"] = x + 20, y + 20
        self.core.pdb[nid]["width"] = w
        self.core.pdb[nid]["height"] = h
        self.core.notes.add(new)

    def menuTool(self):
        """ Opens the tool contextual menu """
        if self.css["context-menu"] == "true":
            self.toolMenu.popup(QtGui.QCursor.pos())

    def moveDialog(self):
        """ Opens subfolder browser dialog """
        self.core.moveDialog(self.path)

    def opacityDecrease(self):
        """ Decreases window opacity """
        self._opacity(-0.1)

    def opacityIncrease(self):
        """ Increases window opacity """
        self._opacity(0.1)

    def pin(self):
        """ Toggles the pin attribute of the note profile """
        current = self.core.pdb[self.id]["pin"]
        self.core.pdb[self.id]["pin"] = not current
        self.setup.status()

    def position(self, index: int, total: int) -> Tuple[int, int]:
        """ Calculates the right position for a new note """
        w, h = self.width(), self.height()
        pos = self.frameGeometry()
        rect = self.core.screen()
        gap = 20

        screen_h = rect.height() - h - (h / 3)  # Available screen rect less clearance
        col_count = int(screen_h / gap) + 1  # Number of notes in each columns
        col_current = int(index / col_count)  # Column # of the current note

        # Drift correction for new columns
        col_drift = gap * col_count
        x_offset = (w - col_drift) * col_current
        y_offset = - col_drift * col_current

        # Set the anchor at the screen center for few notes, at left for many
        if int(total / col_count) > 0:
            pos.moveTopLeft(rect.topLeft())
        else:
            pos.moveCenter(rect.center())
            pos.moveTop(rect.top())

        # Apply drift and offset corrections
        drift = gap * index
        x = int(pos.x() + drift + x_offset)
        y = int(pos.y() + drift + y_offset)
        return x, y

    def reset(self):
        """ Resets window geometry """
        self.resetSize()
        self.resetPosition()

    def resetPosition(self):
        """ Moves to the center of the screen """
        rect = self.core.screen()
        pos = self.frameGeometry()
        pos.moveCenter(rect.center())
        self.move(pos.x(), pos.y())

    def resetSize(self):
        """ Sets size to profile default """
        width = self.core.sdb["profile default"]["width"]
        height = self.core.sdb["profile default"]["height"]
        self.resize(width, height)

    def resizeToContent(self):
        """ Resizes Note to best fit text width and height """
        def resize(self):
            screenMaxWidth = self.core.screen().width() / 3
            screenMaxHeight = self.core.screen().height() / 1.5

            # Determine the 'ideal' width
            lines = [line for line in self.body.toPlainText().splitlines()]
            textMaxWidth = self.body.fontMetrics().width(max(lines, key=len))  # Pixel width of the longuest line
            width = min(textMaxWidth, screenMaxWidth) * 1.105  # Add 10.5% for clearance
            self.resize(width, self.height())

            # Get the line count at the new width, convert to pixel height
            lineCount = self.body.document().blockCount()
            height = self.body.fontMetrics().height() * lineCount

            # Add widgets margins and bars height
            for widget in (self.titleLabel, self.msgbarFrame, self.toolbarFrame, self.hotbarFrame):
                height += widget.height()

            for widget in (self, self.body, self.titleLabel, self.msgbarFrame,
                           self.toolbarFrame, self.hotbarFrame):
                margins = widget.contentsMargins()
                width += margins.left() + margins.right()
                height += margins.top() + margins.bottom()

            # Clamp the note to a reasonable size
            width = min(width, screenMaxWidth)
            height = min(height, screenMaxHeight)

            # Apply new size and move cursor to top
            self.resize(width, height)

        self.unroll()
        if self.mode == "image":
            self.resizeFit()

        elif "toPlainText" in dir(self.body):
            if self.body.toPlainText():
                wrap = self.body.lineWrapMode()
                self.body.setLineWrapMode(self.body.WidgetWidth)
                resize(self)
                resize(self)  # Two calls are needed for some odd cases
                self.body.setLineWrapMode(wrap)
                self._cursorToTop()
            else:
                self.resetSize()

    def restoreGeometry(self):
        """ Restores the size, position, wrap mode and opacity from profile """
        pos = self.core.pdb[self.id]["position"]
        width = self.core.pdb[self.id]["width"]
        height = self.core.pdb[self.id]["height"]
        opacity = self.core.pdb[self.id]["opacity"]
        wrap = self.core.pdb[self.id]["wrap"]

        self.move(*pos)
        self.resize(width, height)
        self.setWindowOpacity(opacity)
        if self.mode in ("plain", "html"):
            wrap = self.body.WidgetWidth if wrap else self.body.NoWrap
            self.body.setLineWrapMode(wrap)

    def roll(self):
        """ Minimizes window to the titlebar height """
        if self.body.isVisible():
            self.saveGeometry()
            self.toolbarFrame.hide()
            self.msgbarFrame.hide()
            self.hotbarFrame.hide()
            self.body.hide()
            QtCore.QTimer.singleShot(0, self._minimize)  # resize(width, 0) on next loop

    def saveGeometry(self):
        """ Saves the size, position, wrap mode and opacity to profile """
        x, y = self.x(), self.y()
        w, h = self.width(), self.height()
        opacity = round(self.windowOpacity(), 2)
        self.core.pdb[self.id]["position"] = [x, y]
        self.core.pdb[self.id]["opacity"] = opacity

        if self.body.isVisible():  # Prevents saving rolled size
            self.core.pdb[self.id]["width"] = w
            self.core.pdb[self.id]["height"] = h

        if self.mode in ("plain", "html"):
            self.core.pdb[self.id]["wrap"] = bool(self.body.lineWrapMode())

    def setTitle(self, title: str):
        """ Sets note title """
        try:
            self.titleLabel.setText(title)
        except AttributeError:
            pass

    def unload(self):
        """ Unloads a sub-note or hide a note at root directory """
        self.core.ndb["favorites"].discard(self.id)
        if self.path.relative_to(ConfigDirs.NOTES).parts[:-1]:
            self.core.notes.close(self.path)  # Unload from folder
        else:
            self.hide()  # Notes at root are always loaded
            self._blank()  # Still, removes the note if its empty

    def unroll(self):
        """ Restores full window size """
        if not self.body.isVisible():
            self.toolbarFrame.show()
            self.msgbarFrame.show()
            self.hotbarFrame.show()
            self.body.show()
            width = self.core.pdb[self.id]["width"]
            height = self.core.pdb[self.id]["height"]
            self.resize(width, height)

    def _blank(self):
        """ Removes note if empty """
        if not self.protected and self.core.sdb["clean"]["blanks"]:
            try:
                if not self.body.toPlainText():
                    self.path.unlink()
                    self.deleteLater()
                    log.info(f"{self.id} : Removed empty note")
                    self.core.setup.lint()
            except (FileNotFoundError, PermissionError, AttributeError):
                pass

    def _cursorToTop(self):
        """ Moves the cursor at the beginning of the document """
        cursor = self.body.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        self.body.setTextCursor(cursor)

    def _initNoteWindow(self, path):
        """ Inits menus and setups window properties """
        self.setup = NoteSetup(self, path)
        self.core.pdb[self.id]["mode"] = self.mode
        self.protected = False  # Protects empty note from deletion on mode change
        self.modeMenu = ModeMenu(self)
        self.paletteMenu = PaletteMenu(self)
        self.styleMenu = StyleMenu(self)
        self.toolMenu = ToolMenu(self)
        self._skipTaskbar()
        self.restoreGeometry()

    def _menuMode(self):
        """ Opens the mode contextual menu """
        self.modeMenu.popup(QtGui.QCursor.pos())

    def _menuMove(self):
        """ Opens the move contextual menu """
        self.moveMenu.popup(QtGui.QCursor.pos())

    def _menuPalette(self):
        """ Opens the palette contextual menu """
        self.paletteMenu.popup(QtGui.QCursor.pos())

    def _menuStyle(self):
        """ Opens the style contextual menu """
        self.styleMenu.popup(QtGui.QCursor.pos())

    def _minimize(self):
        """ Resize note window to the titlebar height """
        self.resize(self.width(), 0)

    def _opacity(self, inc: float):
        """ Adjusts window opacity """
        opacity = round(self.windowOpacity() + inc, 2)
        opacity = opacity if opacity > 0.1 else 0.1
        self.setWindowOpacity(opacity)

    def _saveAs(self):
        """ Opens a save as dialog -> .txt or .png """
        title = "Save note as"
        dest = QtWidgets.QFileDialog.getSaveFileName(self, title, self.name, self.path.suffix)[0]
        if dest:
            dest = f"{dest}{self.path.suffix}"
            try:
                shutil.copy(self.path, dest)
            except PermissionError:
                log.exception(f"Could not copy file to {dest}")

    def _skipTaskbar(self):
        """ Hides the note from the system taskbar """
        skip = self.core.sdb["general"]["skip taskbar"]
        if skip and sys.platform.startswith("win"):
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

        elif sys.platform.startswith("linux"):
            # X11: Manually set the _NET_WM_STATE_SKIP_TASKBAR flag on each window
            # Avoid various WM issues related with WA_X11NetWmWindowType*
            # Use of external process 'xprop' since no skip flag exist in Qt yet
            ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
            wid = ctypes.pythonapi.PyCapsule_GetPointer(self.winId().ascapsule(), None)
            cmd = f"-id {wid} -f _NET_WM_STATE 32a -set _NET_WM_STATE _NET_WM_STATE_SKIP_TASKBAR"
            self.xprop = QtCore.QProcess()
            self.xprop.setProgram("xprop")
            self.xprop.setArguments(cmd.split())

    def _swap(self):
        """ Swaps note status among idle, favorite and pinned """
        if self.id in self.core.ndb["favorites"]:
            self.core.ndb["favorites"].discard(self.id)
            self.pin()
        elif self.core.pdb[self.id]["pin"]:
            self.pin()
        else:
            self.core.ndb["favorites"].add(self.id)
        self.setup.status()


class NoteSetup:
    """ Setups instances and variables for Note class """
    def __init__(self, note, path):
        self.note = note
        self.core = note.core
        self.uid(path)
        self.top()
        self.pdb()
        self.css()
        self.icons()
        self.actions()
        self.bottom()
        self.grid()
        self.signals()
        note.setTitle(path.stem)

    def actions(self):
        """ Fetches notes actions for the current mode """
        c, n = self.core, self.note
        n.actions = self.actionsFromMode(c, n.mode, note=n)

    @staticmethod
    def actionsFromMode(core, mode: str = "all", note: Note = None) -> dict:
        """ Returns available actions for one or all modes """
        class NoteMock:
            def __init__(self):
                self.notes = self
                self.body = self

            def __getattr__(self, *args) -> Callable:
                return lambda: None

        def bicolor(key):
            return Tuples.NoteIcons(note.icons.menu.get(key), note.icons.toolbar.get(key))

        c = core
        n = note if note else NoteMock()
        icons = bicolor if note else lambda key: core.icons.get(key)
        Action = Tuples.Action

        actions = {
            "activate": Action("Activate", icons("activate"), n.activateWindow),
            "delete": Action("Delete", icons("delete"), c.notes.delete),
            "duplicate": Action("Duplicate", icons("duplicate"), n.duplicate),
            "hide": Action("Hide", icons("hide"), n.hide),
            "mode": Action("Mode", icons("mode"), n._menuMode),
            "move": Action("Move", icons("move"), n.moveDialog),
            "new": Action("New note", icons("new"), c.notes.new),
            "opacity+": Action("Increase opacity", icons("opacity_increase"), n.opacityIncrease),
            "opacity-": Action("Decrease opacity", icons("opacity_decrease"), n.opacityDecrease),
            "open": Action("Open in file manager", icons("folder_open"), c.fileManager),
            "pin": Action("Pin", icons("pin"), n.pin),
            "raise": Action("Raise", icons("raise"), n.raise_),
            "refresh": Action("Refresh", icons("refresh"), n.style),
            "rename": Action("Rename", icons("rename"), c.notes.rename),
            "reset": Action("Reset geometry", icons("reset"), n.reset),
            "resize": Action("Resize to content", icons("fit"), n.resizeToContent),
            "roll": Action("Roll", icons("roll"), n.roll),
            "save as": Action("Save as", icons("save_as"), n._saveAs),
            "separator": Action("Separator", icons("separator"), lambda: None),
            "style": Action("Style", icons("style"), n._menuStyle),
            "swap": Action("Swap status", icons("swap"), n._swap),
            "palette": Action("Palette", icons("palette"), n._menuPalette),
            "unload": Action("Unload", icons("hide"), n.unload),
            "unroll": Action("Unroll", icons("unroll"), n.unroll),
        }

        if mode in ("plain", "html", "all"):
            lockIcon = "unlock" if n.readOnly else "lock"
            actions.update({
                "antidote": Action("Antidote", icons("spelling"), n.body.antidote),
                "capitalize": Action("Capitalize", icons("capitalize"), n.body.capitalize),
                "copy": Action("Copy plain text", icons("copy"), n.body.copyPlain),
                "cut": Action("Cut plain text", icons("cut"), n.body.cutPlain),
                "line delete": Action("Delete line", icons("line_delete"), n.body.lineDelete),
                "line down": Action("Move line downward", icons("line_down"), n.body.lineDown),
                "line duplicate": Action("Duplicate line", icons("add"), n.body.lineDuplicate),
                "line end": Action("Go to end of line", icons("line_end"), n.body.lineEnd),
                "line start": Action("Go to start of line", icons("line_start"), n.body.lineStart),
                "line up": Action("Move line upward", icons("line_up"), n.body.lineUp),
                "lock": Action("Lock content (read-only)", icons("lock"), n.lock),
                "lock|unlock": Action("Toggle read-only", icons(lockIcon), n.toggleLock),
                "lowercase": Action("Lowercase", icons("lowercase"), n.body.lowercase),
                "paste": Action("Paste", icons("paste"), n.body.paste),
                "redo": Action("Redo", icons("redo"), n.body.redo),
                "save": Action("Save", icons("save"), n.save),
                "search": Action("Find and replace", icons("search"), n.search),
                "select all": Action("Select all", icons("select_all"), n.body.selectAll),
                "shuffle": Action("Shuffle", icons("shuffle"), n.body.lineShuffle),
                "sort": Action("Sort", icons("sort"), n.body.lineSort),
                "special paste": Action("Special paste", icons("paste_special"), n.body.pasteSpecial),
                "swapcase": Action("Swapcase", icons("swapcase"), n.body.swapcase),
                "titlecase": Action("Titlecase", icons("titlecase"), n.body.titlecase),
                "undo": Action("Undo", icons("undo"), n.body.undo),
                "unlock": Action("Unlock content (read-write)", icons("unlock"), n.unlock),
                "uppercase": Action("Uppercase", icons("uppercase"), n.body.uppercase),
                "wrap": Action("Word wrap", icons("wrap"), n.body.wrap),
                "zoom in": Action("Zoom in", icons("zoom_in"), n.body.zoomIn),
                "zoom out": Action("Zoom out", icons("zoom_out"), n.body.zoomOut),
            })

        if mode in ("html", "all"):
            actions.update({
                "bold": Action("Bold", icons("bold"), n.body.bold),
                "clear format": Action("Clear formatting", icons("clear_format"), n.body.clearFormat),
                "copy rich": Action("Copy rich text", icons("copy"), n.body.copy),
                "cut rich": Action("Cut rich text", icons("cut"), n.body.cut),
                "highlight": Action("Highlight", icons("highlight"), n.body.highlight),
                "italic": Action("Italic", icons("italic"), n.body.italic),
                "strike": Action("Strikethrough", icons("strike"), n.body.strike),
                "underline": Action("Underline", icons("underline"), n.body.underline),
            })

        if mode in ("image", "all"):
            lockIcon = "lock" if n.keepAspectRatio else "unlock"
            actions.update({
                "aspect ratio": Action("Keep aspect ratio", icons(lockIcon), n.toggleAspectRatio),
                "fit": Action("Resize to fit screen", icons("fit"), n.resizeFit),
                "original": Action("Original size", icons("size_original"), n.resizeOriginal),
                "scale": Action("Restore aspect ratio", icons("aspect_ratio"), n.restoreAspectRatio),
            })

        if mode in ("console", "all"):
            actions.update({
                "reload": Action("Reload", icons("reset"), n.reload),
            })

        return actions

    def bottom(self):
        """ Organizes bottom bar layout """
        c, n = self.core, self.note

        # Message bar
        n.msgbarFrame = QtWidgets.QFrame()
        n.msgbarLayout = QtWidgets.QHBoxLayout()
        n.msgbarLayout.setContentsMargins(0, 0, 0, 0)
        n.msgbarLayout.setSpacing(0)
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        if c.sdb["message bar"]["folder"]:
            n.folderLabel = FolderLabel(n)
            n.msgbarLayout.addWidget(n.folderLabel)
        n.msgbarLayout.addItem(spacer)

        # Toolbar
        n.leftSpacer = ToolbarSpacer()
        n.rightSpacer = ToolbarSpacer()
        n.toolbarFrame = QtWidgets.QFrame()
        n.toolbarLayout = QtWidgets.QHBoxLayout()
        n.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        n.toolbarLayout.setSpacing(0)

        n.toolbarLayout.addWidget(n.leftSpacer)
        n.tools = {}
        for action in c.sdb["toolbar menus"][n.mode]:
            if action == "separator":
                separator = QtWidgets.QLabel(":")
                separator.setObjectName("toolbar-separator")
                n.toolbarLayout.addWidget(separator)
            else:
                try:
                    n.tools[action] = ToolButton(n, action)
                    n.toolbarLayout.addWidget(n.tools[action])
                except KeyError:
                    log.exception(f"Invalid note menu option '{action}'")
        n.toolbarLayout.addWidget(n.rightSpacer)

        # Hotbar
        sizeGrips = SizeGrip(n, "left"), SizeGripVertical(n), SizeGrip(n, "right")
        n.sizeGrips = Tuples.SizeGrips(*sizeGrips)
        n.hotbarFrame = QtWidgets.QFrame()
        n.hotbarLayout = QtWidgets.QHBoxLayout()
        n.hotbarLayout.setContentsMargins(0, 0, 0, 0)
        n.hotbarLayout.setSpacing(0)

        n.hotbarLayout.addWidget(n.sizeGrips.left)
        n.hotbarLayout.addWidget(HotbarSpacer())
        n.hotbarLayout.addWidget(n.sizeGrips.center)
        n.hotbarLayout.addWidget(HotbarSpacer())
        n.hotbarLayout.addWidget(n.sizeGrips.right)

        # Layout
        n.toolbarFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        n.toolbarFrame.setLayout(n.toolbarLayout)
        n.toolbarFrame.setObjectName("toolbar-frame")

        n.msgbarFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        n.msgbarFrame.setLayout(n.msgbarLayout)
        n.msgbarFrame.setObjectName("msgbar-frame")
        if c.sdb["message bar"]["folder"]:
            n.folderLabel.update()

        n.hotbarFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        n.hotbarFrame.setLayout(n.hotbarLayout)
        n.hotbarFrame.setObjectName("hotbar-frame")

    def css(self):
        """ Updates combined stylesheets and NoteDecorations{} CSS selectors """
        c, n = self.core, self.note
        c.setup.css()  # Reloads global.css
        profile = c.pdb[n.id]

        # Stylesheet(target, fallback)
        style = Tuples.Stylesheet(ConfigDirs.STYLES / profile["style"], RootFiles.DEFAULT_STYLE)
        palette = Tuples.Stylesheet(ConfigDirs.PALETTES / profile["palette"], RootFiles.DEFAULT_PALETTE)

        # Combines NoteDecorations{} CSS Selector from global and profile stylesheets
        sheets = []
        for css in (style, palette):
            sheets.append(css.profile if css.profile.is_file() else css.fallback)
        n.css = c.getNoteDecorationsCSS(*sheets)

        # Combines and apply profile stylesheets
        heap = ""
        for s in sheets:
            with open(s, encoding="utf-8") as f:
                heap += f.read()
        n.setStyleSheet(heap)

        sheets = ", ".join([str(s) for s in sheets])
        log.debug(f"{n.id} : Loaded CSS from '{sheets}'")

    def grid(self):
        """ Organizes all widgets sublayouts into the grid layout """
        n = self.note
        n.gridLayout = QtWidgets.QGridLayout(n)
        n.gridLayout.setSpacing(0)
        n.gridLayout.setContentsMargins(0, 0, 0, 0)
        n.gridLayout.addWidget(n.statusButton, 0, 0, 1, 1)
        n.gridLayout.addWidget(n.titleLabel, 0, 1, 1, 1)
        n.gridLayout.addWidget(n.closeButton, 0, 2, 1, 1)
        n.gridLayout.addWidget(n.msgbarFrame, 2, 0, 1, 3)
        n.gridLayout.addWidget(n.toolbarFrame, 3, 0, 1, 3)
        n.gridLayout.addWidget(n.hotbarFrame, 4, 0, 1, 3)

    def icons(self):
        """ Applies a custom foreground color on toolbar icons """
        c, n = self.core, self.note
        toolbarColor = QtGui.QColor(n.css["toolbar-icon"])
        menuColor = QtGui.QColor(n.css["menu-icon"])
        n.icons = Tuples.NoteIcons({}, {})
        for i in c.icons:
            n.icons.toolbar[i] = c.colorize(c.icons[i], toolbarColor)
            n.icons.menu[i] = c.colorize(c.icons[i], menuColor)

    def pdb(self):
        """ Verifies that the profile exist, else create a new one """
        c, n = self.core, self.note
        profiles = c.pdb
        if n.id not in profiles:
            index = len(c.loaded) + 1
            new = deepcopy(c.sdb["profile default"])
            n.resize(new["width"], new["height"])
            profiles[n.id] = new
            profiles[n.id]["position"] = n.position(index, index)

    def signals(self):
        """ Connects contextual menu signals """
        n = self.note
        for widget in (n.titleLabel, n.toolbarFrame, n.hotbarFrame):
            widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(n.menuTool)

    def status(self):
        """ Sets and colorizes the appropriate status icon pixmap """
        c, n = self.core, self.note
        if c.pdb[n.id]["pin"]:
            icon = n.icons.toolbar["pin_title"]
        elif n.id in c.ndb["favorites"]:
            icon = n.icons.toolbar["toggle"]
        else:
            icon = n.icons.toolbar["tray"]

        color = QtGui.QColor(n.css["status-icon"])
        icon = c.colorize(icon, color)
        n.statusButton.setIcon(icon)
        n.setWindowIcon(icon)

    def toolbar(self):
        """ Setups toolbar layout and buttons """
        c, n = self.core, self.note

        # Toolbar alignment
        left = bool(n.css["toolbar-align"] in ("center", "right"))
        right = bool(n.css["toolbar-align"] in ("center", "left"))
        n.leftSpacer.setVisible(left)
        n.rightSpacer.setVisible(right)

        # Toolbar icons
        for action in c.sdb["toolbar menus"][n.mode]:
            try:
                icon = n.tools[action]
                icon.setIcon(n.actions[action].icon.toolbar)
            except KeyError:
                pass

        # Visibility
        visible = n.css["toolbar-visible"] == "true"
        layout = n.toolbarLayout
        for w in (layout.itemAt(i) for i in range(layout.count())):
            w.widget().setVisible(visible)

    def top(self):
        """ Organizes top layout """
        n = self.note
        n.statusButton = TitleStatusButton(n)
        n.titleLabel = TitleLabel(n)
        n.closeButton = TitleCloseButton(n)

    def uid(self, path: Path):
        """ Parses and sets identifiers from note path """
        n = self.note
        n.id = str(path.relative_to(ConfigDirs.NOTES))
        n.path = path
        n.name = path.stem
        n.setTitle(path.stem)


class Polling:
    """ Monitors file changes, loads and saves automatically """
    def __init__(self):
        self.saveTimer = QtCore.QTimer(interval=1000, singleShot=True)
        self.saveTimer.timeout.connect(self.save)
        self.loadTimer = QtCore.QTimer(interval=5000)
        self.loadTimer.timeout.connect(self._loadSlot)
        self.loadTimer.start()

    def load(func: Callable) -> Callable:
        """ Decorator for load function. Loads content, updates hash and timestamp """
        def wrapper(self, *args):
            if not self.path.is_file(): return
            self._load()
            func(self, *args)
            self.saveTimer.stop()
            log.debug(f"{self.id} : Read file content")
        return wrapper

    def save(func: Callable) -> Callable:
        """ Decorator for save function. Stops pending save timer and updates timestamp """
        def wrapper(self, *args):
            self.saveTimer.stop()
            if not self.path.is_file(): return
            func(self, *args)
            self._timestamp()
            log.debug(f"{self.id} : Saved changes")
        return wrapper

    def _frequency(self):
        """ Sets polling frequency; minimizes IO for idle notes """
        i = 250 if self.isVisible() else 5000
        self.loadTimer.setInterval(i)

    def _load(self):
        """ Loads file content, updates checksum and timestamp """
        with open(self.path, encoding="utf-8") as f:
            self.fileContent = f.read()
        self.core.pdb[self.id]["hash"] = self._md5(self.fileContent)
        self._timestamp()

    def _loadSlot(self):
        """ Slot for the auto load timer """
        self._frequency()
        if not self.isVisible(): return
        if not self.path.is_file(): return
        if self.mtime == self.path.stat().st_mtime: return
        log.debug(f"{self.id} : st_mtime mismatch")
        self.load()

    def _md5(self, text: str) -> str:
        """ Computes a MD5 hash from a string """
        h = hashlib.md5(text.encode("utf8"))
        return h.hexdigest()

    def _timestamp(self):
        """ Updates last modification timestamp (inexpensive IO) """
        self.mtime = self.path.stat().st_mtime


class KeyFilter:
    def __init__(self, note):
        self.note = note
        self.core = note.core
        self.blocked = ("ctrl;c", "ctrl;x", "ctrl;v", "ctrl;z", "ctrl;y", "ctrl;a", "ctrl;k",
                        "ctrl;ins", "ctrl;home", "ctrl;end", "shift;ins", "shift;del")

    def execute(self):
        """ Executes the action bound to the pressed hotkey """
        group, action = self.match()
        cmd = {group: [action]}
        if group == "note":
            cmd["note"].append(self.note.path)
        self.log()
        self.core.parser.fromDict(cmd)

    def ignored(self) -> bool:
        """ Verifies if the match should be ignored (override of Qt's default) """
        match = self._compare(self.blocked)
        return bool(match)

    def match(self) -> list:
        """ Verifies if the pressed keys matches an hotkey """
        if not self.core.sdb["general"]["hotkeys"]:
            return None
        hotkeys = self.core.sdb["key events"]
        return hotkeys.get(self._compare(hotkeys))

    def log(self):
        """ Logs hotkey input """
        mods = [m for m in self.modifiers if self.modifiers[m]]
        if not mods: return
        mods = ",".join(mods)
        try:
            self.key.encode("utf8")  # Needed to catch UnicodeEncodeError (surrogates)
            m, k = mods.capitalize(), self.key.capitalize()
            log.debug(f"{self.note.id} : HotkeyEvent : {m};{k}")
        except UnicodeEncodeError:
            pass

    def update(self, event: QtGui.QKeyEvent):
        """ Updates modifiers and key pressed status """
        mod = event.modifiers()
        self.modifiers = {
            "shift": bool(mod & QtCore.Qt.ShiftModifier),
            "ctrl": bool(mod & QtCore.Qt.ControlModifier),
            "alt": bool(mod & QtCore.Qt.AltModifier),
            "meta": bool(mod & QtCore.Qt.MetaModifier),
        }
        key = QtGui.QKeySequence(event.key())
        self.key = key.toString().lower()

    def _compare(self, hotkeys: Iterable) -> str:
        """ Looks through all registered hotkeys to return matches """
        for hk in hotkeys:  # "ctrl,shift;d": ("note", "delete"),
            mods, key = hk.split(";")
            mods = mods.split(",")
            underload = [m for m in mods if not self.modifiers[m]]
            overload = [m for m in self.modifiers if self.modifiers[m] and m not in mods]
            if not underload and not overload and self.key == key:
                return hk
        return None
