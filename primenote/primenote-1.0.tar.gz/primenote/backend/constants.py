#!/usr/bin/python3
import json
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from PyQt5.QtGui import QTextFragment
try:
    from ..__id__ import ID
except (ValueError, ImportError):
    from __id__ import ID

STYLE_DEFAULT = "minimal.css"
PALETTE_DEFAULT = "northern.css"


def configDir() -> Path:
    if sys.platform.startswith("win"):
        return Path.home() / ID
    return Path.home() / ".config" / ID


def notesDir() -> Path:
    paths = configDir() / "paths.json"
    if paths.is_file():
        with open(paths, encoding="utf-8") as f:
            notes = json.load(f).get("notes")
        if notes and Path(notes).is_dir():
            return Path(notes)
    return configDir() / "notes"


@dataclass
class ConfigDirs:
    CFG = configDir()
    NOTES = notesDir()
    ARCHIVES = CFG / "archives"
    LOGS = CFG / "logs"
    PALETTES = CFG / "ui" / "palettes"
    STYLES = CFG / "ui" / "styles"
    TERMINAL = CFG / "ui" / "terminal"
    TRASH = CFG / "trash"
    VIM = CFG / "ui" / "vim"


@dataclass
class ConfigFiles:
    CSS = ConfigDirs.CFG / "ui" / "global.css"
    LOG = ConfigDirs.LOGS / "session.log"
    NOTES = ConfigDirs.CFG / "notes.json"
    PATHS = ConfigDirs.CFG / "paths.json"
    PROFILES = ConfigDirs.CFG / "profiles.json"
    SETTINGS = ConfigDirs.CFG / "settings.json"
    VIM = ConfigDirs.VIM / "vimrc"


@dataclass
class RootDirs:
    ROOT = Path(__file__).parents[1]
    FONTS = ROOT / "ui" / "fonts"
    ICONS = ROOT / "ui" / "icons"
    PALETTES = ROOT / "ui" / "palettes"
    STYLES = ROOT / "ui" / "styles"
    TERMINAL = ROOT / "ui" / "terminal"
    VIM = ROOT / "ui" / "vim"
    WIZARD = ROOT / "ui" / "wizard"


@dataclass
class RootFiles:
    CSS = RootDirs.ROOT / "ui" / "global.css"
    VIM = RootDirs.ROOT / "vim" / "vimrc"
    DEFAULT_STYLE = RootDirs.STYLES / STYLE_DEFAULT
    DEFAULT_PALETTE = RootDirs.PALETTES / PALETTE_DEFAULT


@dataclass
class BrowserMenusData:
    folders: list = field(default_factory=list)
    subactions: list = field(default_factory=list)
    subfolders: dict = field(default_factory=dict)
    subnotes: dict = field(default_factory=dict)


@dataclass
class CentralMenuData:
    items: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    subnotes: list = field(default_factory=list)


@dataclass
class CoreActions:
    tray: dict
    browser: dict


@dataclass
class Cursor:
    pos: int
    anchor: int
    fragment: QTextFragment = None


@dataclass
class Tuples:
    Action = namedtuple("Action", ("label", "icon", "call"))
    Cleaner = namedtuple("Cleaner", ("dir", "delay"))
    Mime = namedtuple("Mime", ("type", "data"))
    Mode = namedtuple("Mode", ("icon", "label"))
    NoteIcons = namedtuple("NoteIcons", ("menu", "toolbar"))
    RegexCSS = namedtuple("RegexCSS", ("selector", "elements", "property"))
    SizeGrips = namedtuple("SizeGrips", ("left", "center", "right"))
    Stylesheet = namedtuple("Stylesheet", ("profile", "fallback"))
