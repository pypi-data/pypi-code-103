#!/usr/bin/python3
import sys
from pathlib import Path
from typing import Tuple
from PyQt5 import QtWidgets, QtGui

try:
    from ..backend import logger
    from ..backend.constants import ConfigDirs, ConfigFiles, Tuples
    from ..plugins import antidote
except (ValueError, ImportError):
    from backend import logger
    from backend.constants import ConfigDirs, ConfigFiles, Tuples
    from plugins import antidote

log = logger.new(__name__)


class ModeMenu(QtWidgets.QMenu):
    def __init__(self, note):
        super().__init__()
        self.core = note.core
        self.note = note

        action = note.actions["mode"]
        self.setTitle("Mode")
        self.setIcon(action.icon.menu)

        self.struct = list()
        for mode in ("plain", "html"):
            if mode != note.mode:
                self.struct.append(ModeAction(self.note, mode))

        if "QTermWidget" in sys.modules:
            if note.mode != "vim":
                self.struct.append(ModeAction(self.note, "vim"))
            if note.mode != "console":
                self.struct.append(ModeAction(self.note, "console"))

        self.addActions(self.struct)
        self.addSeparator()
        self.addAction(ModeActionSetDefault(self.note))


class ModeAction(QtWidgets.QAction):
    def __init__(self, note, mode: str):
        super().__init__(note)
        self.note = note
        self.core = note.core
        self.mode = mode
        self.triggered.connect(self._triggered)
        self.modes = {
            "console": Tuples.Mode(self.core.icons["console"], "Console"),
            "html": Tuples.Mode(self.core.icons["html_regular"], "Rich text"),
            "plain": Tuples.Mode(self.core.icons["plain_regular"], "Plain text"),
            "vim": Tuples.Mode(self.core.icons["vim"], "Vim"),
        }
        self.setIcon(self.modes[mode].icon)
        self.setText(self.modes[mode].label)

    def _triggered(self):
        """ Handler for left click event, sets editing mode """
        self.core.notes.mode(self.note.path, self.mode)


class ModeActionSetDefault(QtWidgets.QAction):
    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self.core = note.core
        self.setText("Set as default")
        self.setIcon(self.core.icons["add"])
        self.triggered.connect(self._triggered)

    def _triggered(self):
        """ Sets default mode for new notes """
        self.core.sdb["profile default"]["mode"] = self.note.mode
        log.info(f"Default mode set to '{self.note.mode}'")


class CSSMenu(QtWidgets.QMenu):
    def __init__(self, note):
        super().__init__()
        self.note = note
        self.core = note.core
        self.aboutToShow.connect(self.refresh)

    def refresh(self):
        """ Finds the installed CSS files and updates the menu entries """
        self.clear()
        self.struct = list()

        self.folder.parent.mkdir(parents=True, exist_ok=True)
        files = [x for x in self.folder.glob("*.css") if x.is_file()]
        for f in sorted(files, key=lambda item: item.stem.lower()):
            self.struct.append(self.action(self.note, path=f))

        self.addActions(self.struct)
        self.addSeparator()
        self.addAction(self.default(self.note))


class CSSAction(QtWidgets.QAction):
    def __init__(self, note, path: Path = ConfigFiles.CSS):
        super().__init__()
        self.note = note
        self.core = note.core
        self.path = path
        self.setText(path.stem.capitalize())
        self.triggered.connect(self._triggered)

    def _save(self):
        """ Save newly selected style to profile """
        css = "" if self.path == ConfigFiles.CSS else self.path.name
        self.core.pdb[self.note.id][self.type] = css

    def _triggered(self):
        """ Handler for left click event """
        self._save()
        self.note.decorate()


class CSSActionSetDefault(QtWidgets.QAction):
    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self.core = note.core
        self.setText("Set as default")
        self.setIcon(self.core.icons["add"])
        self.triggered.connect(self._triggered)

    def _triggered(self):
        """ Handler for left click event, sets style to default """
        css = self.core.pdb[self.note.id][self.type]
        self.core.sdb["profile default"][self.type] = css
        log.info(f"Default {self.type} set to '{css}'")


class PaletteMenu(CSSMenu):
    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self.setTitle("Palette")
        self.setIcon(note.actions["palette"].icon.menu)

        self.folder = ConfigDirs.PALETTES
        self.action = PaletteAction
        self.default = PaletteActionSetDefault


class PaletteAction(CSSAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "palette"
        try:
            self._setIcon()
        except AttributeError:  # Failed to extract fg/bg from stylesheet
            self.setIcon(self.core.icons["rename"])

    def _colors(self, path: Path) -> Tuple[str, str]:
        """ Fetches the colors of a preview icon """
        css = self.core.getNoteDecorationsCSS(path)
        fg, bg = css["preview-fg"], css["preview-bg"]
        return fg, bg

    def _setIcon(self):
        """ Apply custom colors for the preview icons """
        fg, bg = self._colors(self.path)
        pixmap = self.core.icons["rename"].pixmap(16, 16)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_Xor)
        painter.fillRect(pixmap.rect(), QtGui.QColor(bg))
        painter.setCompositionMode(painter.CompositionMode_DestinationOver)
        painter.fillRect(pixmap.rect(), QtGui.QColor(fg))
        painter.end()
        self.setIcon(QtGui.QIcon(pixmap))


class PaletteActionSetDefault(CSSActionSetDefault):
    def __init__(self, note):
        super().__init__(note)
        self.type = "palette"


class StyleMenu(CSSMenu):
    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self.setTitle("Style")
        self.setIcon(note.actions["style"].icon.menu)

        self.folder = ConfigDirs.STYLES
        self.action = StyleAction
        self.default = StyleActionSetDefault


class StyleAction(CSSAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "style"
        self.setIcon(self.core.icons["aspect_ratio"])


class StyleActionSetDefault(CSSActionSetDefault):
    def __init__(self, note):
        super().__init__(note)
        self.type = "style"


class ToolMenu(QtWidgets.QMenu):
    def __init__(self, note):
        super().__init__()
        self.note = note
        self.core = note.core
        self.aboutToShow.connect(self._refresh)

        self.struct = set()
        self.items = {
            "separator": self.addSeparator,
            "mode": ModeMenu,
            "palette": PaletteMenu,
            "style": StyleMenu,
        }

    def _refresh(self):
        """ Updates tools menu on request """
        def validAntidote(key: str) -> bool:
            if key == "antidote":
                return antidote.isInstalled()
            return False

        self.clear()
        self.struct.clear()
        menu = self.core.sdb["context menus"][self.note.mode]
        for i in menu:
            try:  # Add submenus
                menu = self.items[i](self.note)
                self.addMenu(menu)
                self.struct.add(menu)
            except KeyError:  # Add actions
                if not i == "antidote" or validAntidote(i):
                    action = self.note.actions[i]
                    tool = ToolAction(self.note, action)
                    self.addAction(tool)
                    self.struct.add(tool)
            except TypeError:
                self.addSeparator()


class ToolAction(QtWidgets.QAction):
    def __init__(self, note, action: Tuples.Action):
        super().__init__()
        self.note = note
        self.action = action
        self.setText(action.label)
        self.setIcon(self.action.icon.menu)
        self.triggered.connect(self._triggered)

    def _triggered(self, event):
        """ Handler for left click event, calls an action """
        log.info(f"{self.note.id} : {self.action.label}")
        try:
            self.action.call(self.note.path)
        except TypeError:
            self.action.call()
