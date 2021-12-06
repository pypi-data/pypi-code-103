#!/usr/bin/python3
import re
import requests
import shutil
import sys
import zipfile
from argparse import Namespace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List
from PyQt5 import QtWidgets, QtCore, QtGui

try:
    from .__id__ import ID, APP_NAME
    from .__db__ import CSS_DEFAULT, SDB_DEFAULT, NDB_DEFAULT
    from .backend import cli, logger
    from .backend.cli import CommandParser
    from .backend.constants import CoreActions, ConfigDirs, ConfigFiles, RootDirs, RootFiles, Tuples
    from .backend.database import Database
    from .menus.core import CoreMenu, MoveDialog
    from .menus.search import Launcher, Search
    from .menus.wizard import Wizard
    from .notes.console import Console
    from .notes.vim import Vim
    from .notes.plain import Plain
    from .notes.html import HTML
    from .notes.image import Image
    from .settings import Settings
    from .plugins import antidote
except (ValueError, ImportError):
    from __id__ import ID, APP_NAME
    from __db__ import CSS_DEFAULT, SDB_DEFAULT, NDB_DEFAULT
    from backend import cli, logger
    from backend.cli import CommandParser
    from backend.constants import CoreActions, ConfigDirs, ConfigFiles, RootDirs, RootFiles, Tuples
    from backend.database import Database
    from menus.core import CoreMenu, MoveDialog
    from menus.search import Launcher, Search
    from menus.wizard import Wizard
    from notes.console import Console
    from notes.vim import Vim
    from notes.plain import Plain
    from notes.html import HTML
    from notes.image import Image
    from settings import Settings
    from plugins import antidote

HAS_TERMINAL = "QTermWidget" in sys.modules
log = logger.new(__name__)


class Core(QtCore.QObject):
    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()
        self.app = app
        self.clipboard = app.clipboard()
        self.notes = NoteOperations(self)
        self.setup = CoreSetup(self)
        self._loadNotes()
        self.notes.showPinned()
        app.primaryScreenChanged.connect(self.notes.reposition)
        for db in (self.ndb, self.pdb, self.sdb):
            db.track()  # Attach a timer to monitor and save modifications
        log.info("Initialization completed")

    @property
    def loaded(self) -> dict:
        return self.notes.loaded

    def colorize(self, icon: QtGui.QIcon, color: QtGui.QColor) -> QtGui.QIcon:
        """ Applies a custom foreground color on a monochrome QIcon """
        pixmap = icon.pixmap(48, 48)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QtGui.QIcon(pixmap)

    def execute(self, db: str, key: str, path: Path = None):
        """ Translates mouse press events into core or note actions """
        try:
            group, action = self.sdb["mouse events"][db][key]
            cmd = {group: [action]}
            if group == "note":
                cmd["note"].append(path)
            self.parser.fromDict(cmd)
        except (KeyError, ValueError):
            pass

    def fileManager(self, path: Path = ConfigDirs.NOTES):
        """ Opens the default file system manager. Uses xdg-open for Linux or explorer for Windows """
        path = path if path.is_dir() else path.parent
        self.fm.setArguments([str(path)])
        if not self.fm.startDetached()[0]:
            log.warning(f"Could not open directory '{path}'")

    def getNoteDecorationsCSS(self, *paths: Path) -> dict:
        """ Serializes and combines the content of NoteDecorations{} selector from stylesheets """
        css = dict(CSS_DEFAULT)  # Hardcoded defaults
        stylesheets = (ConfigFiles.CSS, *paths)  # global.css, style, palette
        stylesheets = [path for path in stylesheets if path and path.is_file()]
        for s in stylesheets:
            with open(s, encoding="utf-8") as f:
                selector = re.findall(self.regex.selector, f.read())
                elements = re.findall(self.regex.elements, "".join(selector))
            for e in elements:
                css[e[0]] = e[1]
        return css

    def getNotesFiles(self, path: Path) -> list:
        """ Returns a recursive list of note files. Accepts a directory """
        files = []
        for ext in ("txt", "png"):
            files += [f for f in path.rglob(f"*.{ext}") if f.is_file()]
        return files

    def htmlToPlain(self, path: Path):
        """ Converts file HTML to plain unformatted text """
        with open(path, encoding="utf-8") as f:
            html = f.read()
        try:
            new = QtWidgets.QTextEdit()
            new.setHtml(html)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new.toPlainText())
        except PermissionError:
            pass

    def moveDialog(self, path: Path) -> Path:
        """ Opens subfolder browser dialog """
        dialog = MoveDialog(path.name)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new = Path(dialog.selectedFiles()[0]) / path.name
            if new != path:
                new = self.nameIndex(new) if new.exists() else new
                self.notes.move(path, new)

    def nameIndex(self, path: Path) -> Path:
        """ Increments a numeric suffix until a unique name is found """
        taken = [f.stem for f in path.parent.glob("*.txt") if f.exists()]
        taken += [f.stem for f in path.parent.glob("*.png") if f.exists()]
        taken += [f.name for f in path.parent.glob("*") if f.is_dir()]
        title = path.stem
        try:
            index = int(path.stem.rsplit(" ", 1)[1])
            title = path.stem.rsplit(" ", 1)[0]
        except (ValueError, IndexError):
            index = 1

        name = f"{title} {index}"
        while name in taken:
            name = f"{title} {index}"
            index += 1
        new = (path.parent / name).with_suffix(path.suffix)
        return new

    def quit(self, *args):
        """ Closes all notes and saves databases """
        for path in dict(self.loaded):
            self.notes.close(path)
        self.ndb.save()
        self.pdb.save()
        log.info(f"Leaving {APP_NAME}")
        self.app.quit()
        sys.exit(0)

    def searchToggle(self, show: bool = None):
        """ Shows, hides or toggles the note search utility """
        if show is None:
            visible = self.launcher.isVisible()
            self.launcher.setVisible(not visible)
        else:
            self.launcher.setVisible(show)
            self.launcher.activateWindow()

    def setNoteDecorationsCSS(self, prop: str, value: str, path: Path):
        """ Updates and reloads properties into NoteDecorations{} selector of global.css """
        subst = r"\1%s: %s;\3" % (prop, value)
        with open(path, "r+", encoding="utf-8") as f:
            css = re.sub(self.regex.property % prop, subst, f.read())
            f.seek(0)
            f.write(css)
            f.truncate()

    def setMenuIconsColor(self, color: str):
        """ Sets global menu icons color """
        self.setNoteDecorationsCSS("menu-icon", color, ConfigFiles.CSS)
        self.setup.reloadIcons()
        for path, note in self.loaded.items():
            note.decorate()

    def settings(self):
        """ Opens the settings dialog """
        self.settingsDialog = Settings(self)

    def screen(self) -> QtGui.QScreen:
        """ Returns the primary screen geometry """
        screen = self.app.primaryScreen()
        return screen.availableGeometry()

    def screens(self) -> Iterable[QtGui.QScreen]:
        """ Returns the all screens geometry """
        for s in self.app.screens():
            yield s.availableGeometry()

    def trash(self, path: Path):
        """ Moves a file or a folder tree to /trash/ """
        relative = path.relative_to(ConfigDirs.NOTES)
        dest = ConfigDirs.TRASH / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, dest, dirs_exist_ok=True)
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                shutil.move(path, dest)
                log.info(f"Thrashed '{path}'")
            except FileNotFoundError:
                pass

    def wizard(self):
        """ Launches wizard dialog """
        self.wizardDialog = Wizard(self)
        self.wizardDialog.show()

    def _dropEvent(self, path: Path, mime: Tuples.Mime):
        """ Handler for Mime objects parsed in a Note dropEvent. Accepts filesystem or web URL """
        if path not in self.loaded:
            return  # Avoid race condition while saving dropped pixmap

        note = self.loaded[path]
        log.info(f"{note.id} : DropEvent : {mime}")

        if mime.type == "image":
            log.info(f"{note.id} : DropEvent : Saving dropped pixmap ...")
            self._savePNG(mime)
            if path.stat().st_size == 0:
                self.notes.close(note.path)
        elif mime.type == "text":
            if note.mode in ("plain", "html", "vim"):
                note.drop(mime)

    def _loadNotes(self):
        """ Loads local notes along with previously loaded sub-notes """
        for f in list(self.ndb["loaded"]):  # Sub-notes
            self.notes.add((ConfigDirs.NOTES / f), show=False)

        # Notes database root directory (non-recursive)
        files = [f for f in ConfigDirs.NOTES.glob("*.txt") if f.is_file()]
        files += [f for f in ConfigDirs.NOTES.glob("*.png") if f.is_file()]
        for f in files:
            self.notes.add(f, show=False)

    def _popupMenu(self):
        """ Opens the main contextual menu """
        pos = QtGui.QCursor.pos()
        self.tray.menu.popup(pos)

    def _savePNG(self, mime: Tuples.Mime):
        """ Saves and loads a PNG file from a Mime object pixmap """
        name = self.sdb["general"]["default name"] + ".png"
        new = self.nameIndex(ConfigDirs.NOTES / name)
        f = QtCore.QFile(str(new))
        f.open(QtCore.QIODevice.WriteOnly)
        mime.data.save(f, "PNG")
        self.notes.add(new)


class CoreSetup:
    """ Setups instances and variables for Core class """
    def __init__(self, core):
        self.core = core
        firstUsage = not ConfigFiles.SETTINGS.is_file()

        self.regex()
        self.database()
        self.RecordKeeping(core)
        self.lint()
        self.fonts()
        self.icons()
        self.actions()
        self.extra()
        self.plugins()
        if firstUsage:
            core.wizard()

    def actions(self):
        """ Translates action names into labels, icons and function calls """
        c = self.core
        Action = Tuples.Action

        c.actions = CoreActions({
            # Core actions
            "folders list": Action("Folders tree", c.icons["folder_active"], lambda: None),
            "hide": Action("Hide all", c.icons["hide"], c.notes.hideAll),
            "load": Action("Load folders", c.icons["load_folders"], c.notes.loadAllFolders),
            "menu": Action("Show main menu", c.icons["tray"], c._popupMenu),
            "new": Action("New note", c.icons["new"], c.notes.new),
            "notes list": Action("Orphan notes list", c.icons["plain_regular"], lambda: None),
            "open": Action("Open in file manager", c.icons["folder_open"], c.fileManager),
            "quit": Action("Quit", c.icons["quit"], c.quit),
            "reset": Action("Reset positions", c.icons["reset"], c.notes.reset),
            "reverse": Action("Reverse all", c.icons["reverse"], c.notes.toggleAll),
            "search": Action("Search repository", c.icons["search"], c.searchToggle),
            "separator": Action("Separator", c.icons["separator"], lambda: None),
            "settings": Action("Settings", c.icons["settings"], c.settings),
            "show": Action("Show all", c.icons["show"], c.notes.showAll),
            "toggle": Action("Toggle favorites", c.icons["toggle"], c.notes.toggleFavorites),
            "unload": Action("Unload folders", c.icons["unload_folders"], c.notes.unloadAllFolders),
            "wizard": Action("Setup wizard", c.icons["wizard"], c.wizard),
        }, {
            # Browser actions
            "delete": Action("Delete folder", c.icons["delete"], c.notes.delete),
            "load": Action("Load all", c.icons["load_folders"], c.notes.add),
            "move": Action("Move folder", c.icons["move"], c.moveDialog),
            "new": Action("New note", c.icons["new"], c.notes.new),
            "open": Action("Open in file manager", c.icons["folder_open"], c.fileManager),
            "rename": Action("Rename folder", c.icons["rename"], c.notes.rename),
            "separator": Action("Separator", c.icons["separator"], lambda: None),
            "show": Action("Show all", c.icons["show"], c.notes.showAll),
            "unload": Action("Unload all", c.icons["unload_folders"], c.notes.close),
        })
        log.info("Loaded core actions")

    def css(self):
        """ Updates global.css stylesheet """
        sheet = ConfigFiles.CSS if ConfigFiles.CSS.is_file() else RootFiles.CSS
        with open(sheet, encoding="utf-8") as f:
            self.core.app.setStyleSheet(f.read())
        log.debug(f"Loaded CSS from '{sheet}'")

    def database(self):
        """ Initializes databases and favorites notes """
        self.core.pdb = Database(ConfigFiles.PROFILES, default={})  # Profiles
        self.core.sdb = Database(ConfigFiles.SETTINGS, default=SDB_DEFAULT)  # Settings
        self.core.ndb = Database(ConfigFiles.NOTES, default=NDB_DEFAULT)  # Notes
        self.core.ndb["favorites"] = set(self.core.ndb["favorites"])

    def extra(self):
        """ Setups auxiliaries instances """
        self.core.parser = CommandParser(self.core)
        self.core.tray = TrayIcon(self.core)

        # Drop filter
        self.core.dropFilter = DropFilter()
        self.core.dropThread = QtCore.QThread()
        self.core.dropFilter.moveToThread(self.core.dropThread)
        self.core.dropFilter.mime.connect(self.core._dropEvent)
        self.core.dropThread.start()

        # File manager
        self.core.fm = FileManager()
        log.info("Loaded auxiliaries objects")

        # Search file utilities
        self.core.search = Search(self.core)
        self.core.launcher = Launcher(self.core)

    def fonts(self):
        """ Loads Liberation fonts for cross-platform stylesheets """
        fonts = [str(f) for f in RootDirs.FONTS.glob("*.ttf") if f.is_file()]
        for f in fonts:
            QtGui.QFontDatabase.addApplicationFont(f)
        log.info("Loaded fonts")

    def icons(self):
        """ Loads and colorize all SVG icons """
        css = self.core.getNoteDecorationsCSS()
        tray = QtGui.QColor(css.get("tray-icon", None))
        menu = QtGui.QColor(css["menu-icon"])

        self.core.icons = {}
        for path in [x for x in RootDirs.ICONS.glob("*.svg") if x.is_file()]:
            icon = QtGui.QIcon(str(path))
            color = tray if (path.stem == "tray" and tray.isValid()) else menu
            self.core.icons[path.stem] = self.core.colorize(icon, color)
        log.info("Loaded icons")

    def lint(self):
        """ Removes dead keys from databases """
        for path in dict(self.core.loaded):  # Loaded notes
            if not path.exists():
                del self.core.loaded[path]

        for nid in set(self.core.ndb["favorites"]):
            path = ConfigDirs.NOTES / nid
            if not path.exists():
                self.core.ndb["favorites"].discard(nid)

        for nid in dict(self.core.pdb):  # Profiles database
            path = ConfigDirs.NOTES / nid
            if not path.is_file():
                del self.core.pdb[nid]

        log.debug("Cleaned orphan databases entries")

    def plugins(self):
        """ Loads third-party software """
        if sys.platform.startswith("win"):
            self.core.antidote = antidote.getHandler(APP_NAME, init=True, silent=True)
        log.info("Loaded plugins")

    def regex(self):
        """ Pre-compiles CSS regex patterns """
        self.core.regex = \
            Tuples.RegexCSS(re.compile(r"(?:NoteDecorations\s*\{\s*)([\s\S]*?)(?:\s*\})"),  # NoteDecorations{} selector
                            re.compile(r"([^:;\s]+)\s?:\s?([^;\s]+)(?=;)"),  # Elements within a selector
                            r"(NoteDecorations\s*\n*{[\w\W]*)%s\s*:\s*(#[abcdefABCDEF\d]{6}|\w+\s*);([\w\W]*?})")  # Property

    def reloadIcons(self):
        """ Reload icons in core and loaded notes """
        self.icons()
        self.actions()
        for path in self.core.loaded:
            note = self.core.loaded[path]
            note.setup.actions()

    class RecordKeeping:
        def __init__(self, core):
            self.core = core
            self.blanks()
            self.clean()
            self.archive()

        def archive(self):
            """ Creates a new archive if required """
            if self.core.sdb["archives"]["frequency"]:
                ConfigDirs.ARCHIVES.mkdir(parents=True, exist_ok=True)
                limit = datetime.now() - timedelta(days=self.core.sdb["archives"]["frequency"])
                archives = [self._ctime(f) for f in ConfigDirs.ARCHIVES.glob("*.zip")]
                if not archives or max(archives) < limit:
                    self._saveArchive()

        def blanks(self):
            """ Removes empty files and folders """
            if self.core.sdb["clean"]["blanks"]:
                self._delete(f for f in ConfigDirs.NOTES.rglob("*") if f.stat().st_size == 0)
                self._delete(f for f in ConfigDirs.NOTES.rglob("*") if f.is_dir() and self._isEmpty(f))

        def clean(self):
            """ Removes old files from trash, archives and logs folders """
            tasks = (Tuples.Cleaner(ConfigDirs.TRASH, self.core.sdb["clean"]["trash"]),
                     Tuples.Cleaner(ConfigDirs.LOGS, self.core.sdb["clean"]["logs"]),
                     Tuples.Cleaner(ConfigDirs.ARCHIVES, self.core.sdb["clean"]["archives"]))
            for task in tasks:
                expired = self._expired(task.dir, task.delay)
                self._delete(expired)
            log.info("Cleaned trashes, logs and archives")

        def _ctime(self, path: Path) -> datetime:
            """ Returns the creation time of a file """
            creation = path.stat().st_ctime
            return datetime.fromtimestamp(creation)

        def _delete(self, files: List[Path]):
            """ Deletes a list of files or folders """
            for f in files:
                try:
                    f.unlink()
                    log.info(f"Removed file '{f}'")
                except IsADirectoryError:
                    shutil.rmtree(f)
                    log.info(f"Removed folder '{f}'")
                except (PermissionError, FileNotFoundError):
                    pass

        def _expired(self, path: Path, days: int) -> List[Path]:
            """ Recurses into a directory and returns a list of files older than <days> """
            limit = datetime.now() - timedelta(days=days)
            return [f for f in path.rglob("*") if self._ctime(f) < limit]

        def _isEmpty(self, path: Path):
            """ Verifies if a directory is empty """
            return not [f for f in path.rglob("*") if f.is_file()]

        def _saveArchive(self):
            """ Builds the archive """
            files = []
            if self.core.sdb["archives"]["text"]:
                files += [f for f in ConfigDirs.NOTES.rglob("*.png") if f.is_file()]
            if self.core.sdb["archives"]["image"]:
                files += [f for f in ConfigDirs.NOTES.rglob("*.txt") if f.is_file()]

            if files:
                now = datetime.now()
                path = ConfigDirs.ARCHIVES / f"{now.year:02d}-{now.month:02d}-{now.day:02d}.zip"
                log.info(f"Saving new archive '{path}' ...")
                self._zip(files, path)

        def _zip(self, files: List[Path], path: Path):
            """ Creates a zip file while preserving the file tree """
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as f:
                for file in files:
                    f.write(file, file.relative_to(ConfigDirs.NOTES))


class NoteOperations(QtCore.QObject):
    def __init__(self, core: QtCore.QObject):
        self.loaded = {}
        self.core = core

    @property
    def ndb(self) -> dict:
        return self.core.ndb

    @property
    def pdb(self) -> dict:
        return self.core.pdb

    @property
    def sdb(self) -> dict:
        return self.core.sdb

    def add(self, path: Path, show: bool = True):
        """ Adds Note objects to self.loaded. Accepts a file or a folder tree """
        if path.is_file():
            if path not in self.loaded:
                self._load(path)
                self._saveSubNotes()
                if show:
                    self.loaded[path].show()
                log.info(f"Loaded '{path}'")

        elif path.is_dir():
            for f in self.core.getNotesFiles(path):
                self.add(f)

    def close(self, path: Path):
        """ Cleanly closes Note objects. Accepts a file or a folder tree """
        if path.is_dir():
            for f in self.core.getNotesFiles(path):
                self.close(f)
        elif path in self.loaded:
            self.loaded[path].close()
            self.loaded.pop(path, None)
            self._saveSubNotes()
            log.info(f"Unloaded '{path}'")

    def delete(self, path: Path):
        """ Sends note file to trash. Accepts a file or a folder tree """
        self.close(path)
        self.core.trash(path)

    def hideAll(self):
        """ Hides all but pinned notes """
        for path in dict(self.loaded):
            nid = self.loaded[path].id
            if not self.pdb[nid]["pin"]:
                self.loaded[path].hide()

    def loadAllFolders(self):
        """ Loads all sub-folders """
        self.add(ConfigDirs.NOTES)

    def mode(self, path: Path, mode: str):
        """ Sets a note interface mode (text/console) """
        note = self.loaded[path]
        note.protected = True
        old = note.mode
        self.pdb[note.id]["mode"] = mode
        self.close(path)

        if old == "html":
            self.core.htmlToPlain(path)  # Converts to plain text

        self.add(path)
        log.info(f"{note.id} : Changed mode from '{old}' to '{mode}'")

    def move(self, old: Path, new: Path):
        """ Renames a note or a group of note. Accepts a file or a folder """
        try:
            if old.is_dir():
                for f in old.iterdir():
                    self.move(f, new / f.name)
                shutil.rmtree(old, ignore_errors=True)
            else:
                self._moveNote(old, new)
        except FileExistsError:
            # Name collision; new folder with existing filename ie. /test.txt/
            log.exception(f"File already exists '{new}'")

        self.pdb.save()
        self._saveSubNotes()
        self.ndb.save()

    def new(self, path: Path = ConfigDirs.NOTES):
        """ Create a new text note """
        mode = self.sdb["profile default"]["mode"]
        name = self.sdb["general"]["default name"] + ".txt"
        dest = self.core.nameIndex(path / name)
        if not dest.parent.is_dir():  # Opened from a note action call
            dest = self.core.nameIndex(path.parent / name)  # Use note's parent path instead
        dest.touch()
        self._loadNote(dest, mode)
        self.loaded[dest].show()

    def rename(self, path: Path):
        """ Opens a renaming prompt. Accepts a file or a folder tree """
        relative = path.relative_to(ConfigDirs.NOTES)
        msg = QtWidgets.QInputDialog()
        msg.setFixedSize(280, 120)
        msg.setInputMode(QtWidgets.QInputDialog.TextInput)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(f"Rename '{relative}'")
        msg.setLabelText("Enter the new name:")
        msg.setTextValue(path.stem)

        if msg.exec_() == QtWidgets.QDialog.Accepted:
            new = self._sanitize(msg.textValue(), default=path.stem)
            new = path.parent / (new + path.suffix)
            if new.exists() and new != path:
                new = self.core.nameIndex(new)
            self.move(path, new)
        else:
            new = path

    def reposition(self, screen: QtGui.QScreen):
        """ Moves out of bounds notes to the center of the primary screen """
        if self.sdb["general"]["reposition"]:
            for path in self.loaded:
                note = self.loaded[path]
                if note.isVisible() and not note.onScreen:
                    note.resetPosition()

    def reset(self):
        """ Shows all and resets the geometry of all loaded notes """
        self.showAll()

        total = len(self.loaded)
        for index, path in enumerate(self.loaded, start=1):
            style = self.sdb["profile default"]["style"]
            palette = self.sdb["profile default"]["palette"]
            width = self.sdb["profile default"]["width"]
            height = self.sdb["profile default"]["height"]
            note = self.loaded[path]

            # Adjust image size prior to position calculation
            if note.mode == "image":
                note.setMinimumSize(1, 1)
                note.resize(width, height)

            # Profile and stylesheet update
            pos = note.position(index, total)
            self.pdb[note.id]["width"] = width
            self.pdb[note.id]["height"] = height
            self.pdb[note.id]["position"] = pos
            self.pdb[note.id]["style"] = style
            self.pdb[note.id]["palette"] = palette
            note.decorate()

            # Apply changes
            note.restoreGeometry()
            note.activateWindow()

    def showAll(self, folder: Path = ConfigDirs.NOTES):
        """ Shows all loaded notes relative to a path """
        for path, note in self.loaded.items():
            if folder in path.parents:
                note.show()

    def showPinned(self):
        """ Raises pinned notes on startup """
        if not self.sdb["general"]["minimize"]:
            for path, note in self.loaded.items():
                if self.pdb[note.id]["pin"]:
                    note.show()

    def toggle(self, path: Path):
        """ Show or hide a note """
        if path not in self.loaded:
            self.add(path)
        else:
            isVisible = self.loaded[path].isVisible()
            self.loaded[path].setVisible(not isVisible)

    def toggleAll(self):
        """ Toggles all loaded notes """
        for path in self.loaded:
            self.toggle(path)

    def toggleFavorites(self):
        """ Updates favorites notes list and toggle their visibility """
        def _activatePinned(self):
            for path, note in self.loaded.items():
                if self.pdb[note.id]["pin"]:
                    note.activateWindow()

        def _visiblesSurvey() -> Iterable:
            for path, note in self.loaded.items():
                pinned = self.pdb[note.id]["pin"]
                if note.isVisible() and not pinned:
                    yield path

        def _relative(path: Path) -> str:
            relative = path.relative_to(ConfigDirs.NOTES)
            return str(relative)

        visibles = {_relative(path) for path in _visiblesSurvey()}
        favorites = {path for path in visibles if path in self.ndb["favorites"]}
        favorites = favorites if favorites else visibles
        if visibles:
            self.ndb["favorites"] = {path for path in favorites}
            self.hideAll()
            _activatePinned(self)
        else:
            for path, note in self.loaded.items():
                if _relative(path) in self.ndb["favorites"]:
                    note.show()

    def unloadAllFolders(self):
        """ Unloads all sub-folders """
        folders = [f for f in ConfigDirs.NOTES.glob("*") if f.is_dir()]
        for f in folders:
            self.close(f)

    def _load(self, path: Path):
        """ Creates an image or a text Note instance from a file """
        def _isHTML() -> bool:
            """ Verifies if the note file has HTML content """
            with open(path, encoding="utf-8") as f:
                return f.read().startswith("<!DOCTYPE HTML")

        def _isScript() -> bool:
            """ Verifies if the note file is a script """
            with open(path, encoding="utf-8") as f:
                return bool(re.findall(r"^#!(\/\w+.*)", f.read()))

        nid = str(path.relative_to(ConfigDirs.NOTES))
        isImage = path.suffix == ".png"

        try:  # Existing "mode" attribute in profile
            mode = self.pdb[nid]["mode"]
            if isImage:
                self.loaded[path] = Image(self.core, path)
            else:
                self._loadNote(path, mode)
        except KeyError:  # New note
            if isImage:
                self.loaded[path] = Image(self.core, path, resize=True)
            elif _isHTML():
                self._loadNote(path, "html")
            elif _isScript() and HAS_TERMINAL:
                self._loadNote(path, "console")
            else:
                mode = self.sdb["profile default"]["mode"]  # Default
                self._loadNote(path, mode)

    def _loadNote(self, path: Path, mode: str):
        """ Creates an instance of the desired mode """
        if mode == "html":
            self.loaded[path] = HTML(self.core, path)
        elif mode == "console" and HAS_TERMINAL:
            self.loaded[path] = Console(self.core, path)
        elif mode == "vim" and HAS_TERMINAL:
            self.loaded[path] = Vim(self.core, path)
        else:
            self.loaded[path] = Plain(self.core, path)
        self.loaded[path].shown.connect(self.core.search.attach)
        self.loaded[path].hidden.connect(self.core.search.detach)

    def _moveNote(self, old: Path, new: Path):
        """ Moves a note in the file system and updates all bound identifiers """
        new.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(old, new)
        oid = str(old.relative_to(ConfigDirs.NOTES))
        nid = str(new.relative_to(ConfigDirs.NOTES))

        if old in self.loaded:  # Update loaded list
            self.loaded[new] = self.loaded.pop(old)
            self.loaded[new].setup.uid(new)

            if oid in self.ndb["favorites"]:  # Update favorites
                self.ndb["favorites"].discard(oid)
                self.ndb["favorites"].add(nid)

            if isinstance(self.loaded[new], Vim):  # Notice the Vim server
                self.loaded[new].server.move(new)

        if old in self.core.search.attached:  # Update attached list (search widget)
            self.core.search.attached.remove(old)
            self.core.search.attached.add(new)

        if oid in self.pdb:  # Update the profiles database
            self.pdb[nid] = self.pdb.pop(oid)

        if new in self.loaded:   # Update the message bar
            self.loaded[new].folderLabel.update()
            self.loaded[new].activateWindow()  # Restore window focus

        log.info(f"Moved '{old}' to '{new}'")

    def _sanitize(self, text: str, default: str):
        """ Ensures that the filename are compliant with Windows and POSIX standards """
        illegal = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7",
                   "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9")
        if text.upper() in illegal:
            log.warning(f"Illegal name '{text}'")
            return default

        for c in '\\/:*?"<>|':
            text = text.replace(c, "")
        return text

    def _saveSubNotes(self):
        """ Saves the list of loaded sub-notes to notes database """
        loaded = (path for path in self.loaded if path.relative_to(ConfigDirs.NOTES).parts[:-1])
        loaded = [str(path.relative_to(ConfigDirs.NOTES)) for path in loaded]
        self.ndb["loaded"] = loaded


class DropFilter(QtCore.QObject):
    mime = QtCore.pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        # This URL validator regular expression belongs to Django Software
        # Copyright (c) Django Software Foundation and individual contributors
        # Please read https://github.com/django/django/blob/master/LICENSE
        self.regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ipv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ipv6
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)\Z", re.IGNORECASE)

    @QtCore.pyqtSlot(object, str)
    def filter(self, path: Path, url: str) -> Tuples.Mime:
        """ Returns the type & content of a filesystem or web URL """
        url = self._sanitize(url)
        mime = Tuples.Mime("invalid", url)
        pixmap = QtGui.QPixmap(url)

        if self._isImage(pixmap):
            mime = Tuples.Mime("image", pixmap)

        elif self._isWebURL(url):
            req = self._request(url)
            pixmap.loadFromData(req)
            if self._isImage(pixmap):
                mime = Tuples.Mime("image", pixmap)
        else:
            try:
                with open(url, encoding="utf-8") as f:
                    mime = Tuples.Mime("text", f.read())
            except (UnicodeDecodeError, IsADirectoryError, PermissionError, OSError):
                pass
        self.mime.emit(path, mime)

    def _isImage(self, pixmap: QtGui.QPixmap) -> bool:
        return not pixmap.isNull()

    def _isWebURL(self, url: str) -> bool:
        return re.match(self.regex, url) is not None

    def _request(self, url: str) -> bytes:
        """ Extracts content from a web URL """
        try:
            return requests.get(url, timeout=5).content
        except requests.exceptions.RequestException:
            log.exception(f"Could not retrieve URL content '{url}'")

    def _sanitize(self, text: str) -> str:
        """ Replaces hex codes from a string """
        # ie. Replace '%5B~%5D' to '[~]'
        # %\d{2}       Patterns starting with a %, followed by two digit
        # %\d[a-fA-F]  Patterns starting with a %, followed by one digit and one letter from a to F
        hexChars = re.findall(r"%\d{2}|%\d[a-fA-F]", text)
        for code in hexChars:
            litteral = code.replace("%", "0x")
            litteral = chr(eval(litteral))
            text = text.replace(code, litteral)
        return text


class FileManager(QtCore.QProcess):
    def __init__(self):
        super().__init__()
        self.setStandardOutputFile(QtCore.QProcess.nullDevice())
        self.setStandardErrorFile(QtCore.QProcess.nullDevice())
        if sys.platform.startswith("win"):
            self.setProgram("explorer")
        else:
            self.setProgram("xdg-open")


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.activated.connect(self._clickEvent)

        # SVG to pixmap back-and-forth conversion (KDE compatibility bug)
        css = self.core.getNoteDecorationsCSS()
        if "tray-icon" in css:  # Overrides color if set in global.css
            icon = core.icons["tray"].pixmap(64, 64)
        else:
            icon = str(RootDirs.ICONS / "tray.svg")
            icon = QtGui.QIcon(icon).pixmap(64, 64)
        self.setIcon(QtGui.QIcon(icon))

        # Fires a timer until the tray is available
        self.timer = QtCore.QTimer(singleShot=True, interval=1000)
        self.timer.timeout.connect(self._show)
        self.timer.start(0)

    def _clickEvent(self, button: QtWidgets.QSystemTrayIcon.ActivationReason):
        """ Handler for mouse events on the tray icon """
        key = {
            QtWidgets.QSystemTrayIcon.Trigger: "left",
            QtWidgets.QSystemTrayIcon.MiddleClick: "middle",
        }.get(button)
        self.core.execute("tray", key)

    def _show(self):
        """ Waits until the system tray is available """
        if self.isSystemTrayAvailable():
            self.menu = CoreMenu(self.core)
            self.setContextMenu(self.menu)
            self.show()
        else:
            self.timer.start()


def main(args: Namespace):
    """ Initializes the application """
    app = QtWidgets.QApplication(sys.argv)
    app.setDesktopFileName(ID)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    core = Core(app)
    core.bus = cli.QDBusObject(core)
    core.parser.fromNamespace(args)
    app.exec()


if __name__ == "__main__":
    main()
