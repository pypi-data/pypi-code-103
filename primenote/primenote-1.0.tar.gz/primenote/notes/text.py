#!/usr/bin/python3
import random
import re
import stat
import sys
from pathlib import Path
from typing import Callable, Tuple
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QTextCursor

try:
    from ..__id__ import APP_NAME
    from ..backend import logger
    from ..notes import Note
    from ..menus.bars import MessageLabel
    from ..backend.constants import Cursor, Tuples
    from ..plugins import antidote
except (ValueError, ImportError):
    from __id__ import APP_NAME
    from backend import logger
    from notes import Note
    from menus.bars import MessageLabel
    from backend.constants import Cursor, Tuples
    from plugins import antidote

log = logger.new(__name__)


class AbstractText(Note):
    def __init__(self, note, path: Path):
        super().__init__(note, path)
        self.note = note

    def drop(self, mime: Tuples.Mime):
        """ Handler for dropped text """
        cursor = self.body.textCursor()
        cursor.insertText(mime.data)
        self.save()

    def focusInEvent(self, event):
        """ Loads file content and forwards focus event to Note """
        super().focusInEvent(event)
        if self.path.is_file():
            self._setWriteMode()

    def lock(self):
        """ Sets file permission to read-only """
        self._setReadOnly(True)

    @property
    def readOnly(self) -> bool:
        """ Sets file write permissions for owner, group, others """
        for mask in (stat.S_IWUSR, stat.S_IWGRP, stat.S_IWOTH):
            if self.path.stat().st_mode & mask:
                return False
        return True

    def search(self):
        self.note.search.attach(self.path)
        self.note.search.show()
        self.note.search.activateWindow()

    def toggleLock(self):
        """ Toggles read-only status """
        self._setReadOnly(not self.readOnly)

    def unlock(self):
        """ Sets file permission to read-write """
        self._setReadOnly(False)

    def _setReadOnly(self, enabled: bool):
        """ Sets file permission as read-only or read-write """
        mask = (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        mode = self.path.stat().st_mode
        mode = mode & ~mask if enabled else mode | mask
        try:
            self.path.chmod(mode)
        except PermissionError:
            pass
        self._setWriteMode()

    def _setWriteMode(self):
        """ Updates the read-only / read-write status """
        if self.readOnly != self.body.isReadOnly():
            self.body.setReadOnly(self.readOnly)
            self.setup.css()
            self.setup.actions()
            self.setup.toolbar()


class AbstractTextBody:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dragEnterEvent(self, event):
        """ Allows the implementation of a customized dropEvent handler """
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        """ Handler for dropped text """
        super().dropEvent(event)
        self.note.save()
        self.note.activateWindow()

    def focusInEvent(self, event):
        """ Forwards focus event to Note """
        self.note.focusInEvent(event)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """ Forwards focus event to Note """
        self.note.focusOutEvent(event)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """ Hotkeys handler """
        keyFilter = self.note.keyFilter
        keyFilter.update(event)
        if keyFilter.match():
            keyFilter.execute()
        elif not keyFilter.ignored():
            super().keyPressEvent(event)

    def antidote(self):
        """ Launches Antidote grammar tool """
        if sys.platform.startswith("win"):
            self._antidoteCOM()
        else:
            self._antidoteDBus()

    def capitalize(self):
        """ Capitalize case of the selected text """
        self._setCase(str.capitalize)

    def copyPlain(self):
        """ Copies the selected plain text to system clipboard """
        selected = self.textCursor().selectedText()
        selected = selected.replace("\0", "")  # Remove null bytes
        selected = selected.replace("\u2029", "\n")  # Replace Qt paragraph separators
        self.core.clipboard.setText(selected)

    def cutPlain(self):
        """ Cuts the selected plain text to system clipboard """
        self.copy()
        self.textCursor().removeSelectedText()

    def pasteSpecial(self):
        """ Pastes text from clipboard, replaces newlines with spaces """
        text = self.core.clipboard.text()
        for linebreak in ("\r\n", "\n", "\t", "\r"):
            text = text.replace(linebreak, " ")
        self.insertPlainText(text)

    def lineDelete(self):
        """ Deletes current block along with its newline char """
        Line(self).delete()

    def lineDuplicate(self):
        """ Duplicates current block """
        Line(self).duplicate()

    def lineDown(self):
        """ Shifts current block downward """
        Line(self).moveDown()

    def lineEnd(self):
        """ Moves cursor to end of line """
        Line(self).toEnd()

    def lineUp(self):
        """ Shifts current block upward """
        Line(self).moveUp()

    def lineSort(self):
        """ Sorts or reverse-sorts current block """
        Line(self).sort()

    def lineShuffle(self):
        """ Shuffles current block """
        Line(self).shuffle()

    def lineStart(self):
        """ Moves cursor to start of line """
        Line(self).toStart()

    def lowercase(self):
        """ Lowers the case of the selected text """
        self._setCase(str.lower)

    def swapcase(self):
        """ Swapcase the selected text """
        self._setCase(str.swapcase)

    def titlecase(self):
        """ Titlecase the selected text """
        self._setCase(str.title)

    def uppercase(self):
        """ Uppers the case of the selected text """
        self._setCase(str.upper)

    def wrap(self, state=None):
        """ Toggles or sets text wrap mode """
        if state is None:
            self.wrap(not bool(self.lineWrapMode()))
        else:
            state = self.WidgetWidth if state else self.NoWrap
            self.setLineWrapMode(state)

    def zoomIn(self):
        """ Increases font point size """
        size = self.font().pointSize() + 1
        self.setStyleSheet(f"font-size: {size}pt")

    def zoomOut(self):
        """ Decreases font point size """
        size = max(5, self.font().pointSize() - 1)
        self.setStyleSheet(f"font-size: {size}pt")

    def _antidoteCOM(self):
        try:
            self.core.antidote.correct(self)
        except AttributeError:
            log.error("Could not find Antidote binary")

    def _antidoteDBus(self):
        try:
            self.note.antidote.correct(self)
        except AttributeError:
            try:
                self.note.antidote = antidote.getHandler(APP_NAME, init=True)
                self.note.antidote.correct(self)
            except FileNotFoundError:
                log.error("Could not find Antidote binary")

    def _setCase(self, case: Callable):
        """ Apply a string operation on the selection while preserving text decorations """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        old = Cursor(cursor.position(), cursor.anchor(), cursor.charFormat())  # Save selection

        # Loop over every chars of the selection
        text = case(cursor.selectedText())
        cursor.setPosition(cursor.selectionStart())
        for char in text:
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

            # Apply operation and restore format
            charFormat = cursor.charFormat()
            cursor.insertText(char)
            cursor.mergeCharFormat(charFormat)

        # Restore selection
        if old.anchor < old.pos:  # Anchor at left
            new = Cursor(cursor.position(), old.anchor)
        else:  # Anchor at right
            new = Cursor(old.pos, cursor.position())
        cursor.setPosition(new.anchor)
        cursor.setPosition(new.pos, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        cursor.endEditBlock()

    def _initNoteBody(self, note):
        """ Setups Q_TextEdit properties """
        self.note = note
        self.core = note.core
        self.setFrameStyle(QtWidgets.QFrame.Box)
        self.setAcceptDrops(True)
        self.setTabStopWidth(16)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(note.menuTool)


class Line:
    def __init__(self, body):
        self.body = body
        self.core = body.core
        self.cursor = body.textCursor()
        self._selectBlock()

    def editBlock(func: Callable) -> Callable:
        """ Groups editing operations as a single undo/redo change """
        def wrapper(self, *args):
            self.cursor.beginEditBlock()
            func(self, *args)  # Execute line operation
            self.cursor.endEditBlock()
            self.body.setTextCursor(self.cursor)  # Apply changes
        return wrapper

    @editBlock
    def delete(self):
        """ Deletes current block along with its newline char """
        self.cursor.removeSelectedText()
        direction = QTextCursor.Left if self.cursor.atEnd() else QTextCursor.Right
        self.cursor.movePosition(direction, QTextCursor.KeepAnchor)
        self.cursor.removeSelectedText()

    @editBlock
    def duplicate(self):
        """ Duplicates current block """
        self.cursor.insertFragment(self.selection.fragment)
        self.cursor.insertText("\n")
        self.cursor.insertFragment(self.selection.fragment)
        self._select()

    @editBlock
    def moveDown(self):
        """ Shifts current block downward """
        if self.cursor.blockNumber() == self.body.document().blockCount() - 1:
            self._select()
        else:
            # Remove selection and take preceeding newline character (if any)
            self.cursor.removeSelectedText()
            self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            self.cursor.removeSelectedText()

            # Insert saved text at the line below
            self.cursor.movePosition(QTextCursor.EndOfBlock)
            self.cursor.insertText("\n")
            self.cursor.insertFragment(self.selection.fragment)

            # Select inserted text
            length = len(self.selection.fragment.toPlainText())
            self.cursor.movePosition(QTextCursor.EndOfBlock)
            self.cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, n=length)

    @editBlock
    def moveUp(self):
        """ Shifts current block upward """
        length = len(self.selection.fragment.toPlainText())
        if self.cursor.position() == length:
            self._select()
        else:
            # Remove selection and take preceeding newline character (if any)
            self.cursor.removeSelectedText()
            self.cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            self.cursor.removeSelectedText()

            # Insert saved text at the line above
            self.cursor.movePosition(QTextCursor.StartOfBlock)
            self.cursor.insertFragment(self.selection.fragment)
            self.cursor.insertText("\n")

            # Select inserted text
            self.cursor.movePosition(QTextCursor.Left)
            self.cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, n=length)

    @editBlock
    def shuffle(self):
        """ Shuffles current block """
        self._reorder("shuffle")

    @editBlock
    def sort(self):
        """ Sorts or reverse-sorts current block """
        self._reorder("sort")

    def toEnd(self):
        """ Moves cursor to end of line """
        self.cursor.movePosition(QTextCursor.EndOfBlock)
        self.body.setTextCursor(self.cursor)

    def toStart(self):
        """ Moves cursor to start of line """
        self.cursor.movePosition(QTextCursor.StartOfBlock)
        self.body.setTextCursor(self.cursor)

    def _arrange(self, elements: list, mode: str) -> list:
        """ Returns a list sorted with the choosen algorithm (sort/shuffle) """
        # Sorted alphanumerical list, toggle reverse
        if mode == "sort":
            result = sorted(elements, key=self._sortKey)
            if result == elements:
                result = sorted(elements, key=self._sortKey, reverse=True)
            return result

        # Randomize
        elif mode == "shuffle":
            return random.sample(elements, len(elements))
        return []

    def _reorder(self, mode: str):
        """ Sorts or shuffles current block """
        text = self.selection.fragment.toPlainText()
        lines = text.splitlines()
        if len(lines) == 1:
            sep = self._separator(lines[0])
            parts = lines[0].split(sep) if sep else list(lines[0])
            parts = self._arrange(parts, mode)
            self.cursor.insertText(sep.join(parts))
        else:
            lines = self._arrange(lines, mode)
            for i, line in enumerate(lines):
                newline = "" if i == len(lines) - 1 else "\n"
                self.cursor.insertText(line + newline)
        self._select()

    def _select(self):
        """ Highlights inserted text, place the anchor at block start """
        self.cursor.setPosition(self.selection.pos)
        self.cursor.setPosition(self.selection.anchor, QTextCursor.KeepAnchor)

    def _selectBlock(self):
        """ Extends and delimit the selection area """
        cursor = self.cursor
        self.lineCount = cursor.selectedText().count("\u2029") + 1  # u2029: Qt paragraph separator
        if self.lineCount == 1:
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        else:
            selectionEnd = cursor.selectionEnd()
            cursor.setPosition(cursor.selectionStart())
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.selection = Cursor(cursor.position(), cursor.anchor(), cursor.selection())

    def _separator(self, text: str) -> str:
        """ Returns the separator with the highest occurence (if any) """
        sep = {" ": 0, ",": 0, ";": 0, "|": 0}
        for s in sep:
            sep[s] = text.count(s)
        if sum(sep.values()) > 0:
            return max(sep, key=sep.get)
        return ""

    def _sortKey(self, key: str) -> tuple:
        """ Sorts integers and strings from a list """
        try:
            return (0, int(key))
        except ValueError:
            return (1, key.lower())


class WordsCounter(MessageLabel):
    def __init__(self, note):
        note.body.textChanged.connect(self.update)
        note.body.selectionChanged.connect(self.update)
        self.body = note.body
        super().__init__(note)
        self.setObjectName("msgbar-words")

    def _count(self, text: str) -> Tuple[int, int]:
        """ Counts the amount of words and characters in a string """
        words = len(re.findall(r'\S+', text))
        chars = len(text)
        return (words, chars)

    def _update(self):
        """ Updates the words counter label for the current selection or the whole text """
        cursor = self.body.textCursor()
        prefix, suffix = ("[", "]") if cursor.hasSelection() else ("", "")
        text = cursor.selectedText() if cursor.hasSelection() else self.body.toPlainText()
        words, chars = self._count(text)
        wordsNum = "s" if words > 1 else ""
        charsNum = "s" if chars > 1 else ""
        self.setText(f"{prefix}{words} word{wordsNum}, {chars} character{charsNum}{suffix}")
