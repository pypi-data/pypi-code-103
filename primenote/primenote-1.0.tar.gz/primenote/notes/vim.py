#!/usr/bin/python3
from pathlib import Path
from PyQt5 import QtCore

try:
    from QTermWidget import QTermWidget
except ImportError:
    QTermWidget = QtCore.QObject

try:
    from ..backend import logger
    from ..backend.constants import ConfigDirs, ConfigFiles
    from ..notes import Note
    from ..notes.console import Terminal
except (ValueError, ImportError):
    from backend import logger
    from backend.constants import ConfigDirs, ConfigFiles
    from notes import Note
    from notes.console import Terminal

log = logger.new(__name__)


class Vim(Note):
    mode = "vim"

    def __init__(self, core, path: Path):
        super().__init__(core, path)
        self._initNoteWindow(path)
        self.ref = f"note_{id(self)}"
        self.server = VimServer(self)
        self.body = VimTerminal(self)
        self.gridLayout.addWidget(self.body, 1, 0, 1, 3)

    def drop(self, mime):
        """ Handler for dropped text """
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(mime.data)


class VimTerminal(Terminal):
    def __init__(self, note):
        super().__init__(note, startnow=0)
        args = ["--clean", "--noplugin",
                "--servername", note.ref,
                "--cmd", f"let &rtp.=',{ConfigDirs.VIM}'",
                "-u", str(ConfigFiles.VIM),
                str(note.path)]

        self.setShellProgram("vim")
        self.setArgs(args)
        self.startShellProgram()


class VimServer(QtCore.QProcess):
    def __init__(self, note):
        super().__init__()
        self.note = note
        self.core = note.core
        self.server = ["--servername", note.ref]
        self.setProgram("vim")
        self.setStandardOutputFile(self.nullDevice())
        self.setStandardErrorFile(self.nullDevice())

    def move(self, new: Path):
        """ Updates the current file path in Vim """
        self._send(["--remote-expr", f'execute("cd {new.parent} | edit {new.name}")'])
        self._send(["--remote-expr", 'execute("autocmd TextChanged,TextChangedI <buffer> silent write")'])

    def _log(self, cmd):
        """ Logs commands sent to the server """
        server = " ".join(self.server)
        command = " ".join(cmd)
        log.info(f"{self.note.id} : vim {server} {command}")

    def _send(self, cmd: list):
        """ Sends commands to the server """
        self._log(cmd)
        self.setArguments(self.server + cmd)
        self.start()
        self.waitForFinished(500)
