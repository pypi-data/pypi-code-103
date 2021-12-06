#!/usr/bin/python3
from pathlib import Path
from PyQt5 import QtWidgets

try:
    from ..notes import Polling
    from ..notes.text import AbstractText, AbstractTextBody, WordsCounter
except (ValueError, ImportError):
    from notes import Polling
    from notes.text import AbstractText, AbstractTextBody, WordsCounter


class Plain(AbstractText, Polling):
    mode = "plain"

    def __init__(self, core, path: Path):
        super().__init__(core, path)
        self.core = core
        self.body = Body(self)
        self._initNoteWindow(path)
        self.load()

        self.body.textChanged.connect(self.saveTimer.start)
        self.gridLayout.addWidget(self.body, 1, 0, 1, 3)
        if core.sdb["message bar"]["words"]:
            self.wordsCounter = WordsCounter(self)
            self.msgbarLayout.addWidget(self.wordsCounter)
            self.wordsCounter.update()

    def showEvent(self, event):
        self.loadTimer.start(0)
        super().showEvent(event)

    @Polling.load  # Reads file, updates hash and st_mtime
    def load(self):
        """ Loads file content """
        cursor = self.body.textCursor()
        self.body.setPlainText(self.fileContent)
        self.body.setTextCursor(cursor)

    @Polling.save  # Stops save timer and updates st_mtime
    def save(self):
        """ Saves content to file """
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(self.body.toPlainText())
        except PermissionError:
            pass


class Body(AbstractTextBody, QtWidgets.QPlainTextEdit):
    def __init__(self, note):
        super().__init__()
        self._initNoteBody(note)
        self.setObjectName("plain")
