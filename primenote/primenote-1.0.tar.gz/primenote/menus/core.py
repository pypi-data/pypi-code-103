#!/usr/bin/python3
from pathlib import Path
from typing import Tuple
from PyQt5 import QtCore, QtGui, QtWidgets

try:
    from ..backend import logger
    from ..backend.constants import CentralMenuData, BrowserMenusData, ConfigDirs, Tuples
except (ValueError, ImportError):
    from backend import logger
    from backend.constants import CentralMenuData, BrowserMenusData, ConfigDirs, Tuples

log = logger.new(__name__)


class SubMenu(QtWidgets.QMenu):
    def __init__(self, core, path: Path):
        super().__init__()
        self.core = core
        loaded = self._loadedCount(path)

        icon = "folder_active" if loaded else "folder_inactive"
        icon = self.core.icons[icon]
        self.setIcon(icon)

        title = f"{path.name} ({loaded})" if loaded else f"{path.name}"
        self.setTitle(title)

    def _loadedCount(self, path: Path) -> int:
        """ Returns a recursive notes count from a directory """
        files = self.core.getNotesFiles(path)
        return len([x for x in files if x in self.core.loaded])


class CoreMenu(QtWidgets.QMenu):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.icons = core.icons
        self.aboutToShow.connect(self._refresh)

    def addFoldersList(self):
        """ Inserts QMenus and QActions of the notes browser """
        menus = self._sort(self.browser.folders)
        for m in menus:
            self.addMenu(m)
        self._insertSubMenus()
        self._insertSubActions()

    def addNotesList(self):
        """ Inserts QActions for locals and loaded sub-notes """
        for group in (self.central.notes, self.central.subnotes):
            for action in self._sort(group):
                icon = self.icon(action.path)
                action.setIcon(icon)
                self.addAction(action)

        if not self.central.subnotes and not self.central.notes:
            action = self._noneAction()
            self.addAction(action)

    def icon(self, path: Path) -> QtGui.QIcon:
        """ Returns an icon for a note mode and its active status """
        nid = str(path.relative_to(ConfigDirs.NOTES))
        try:
            mode = self.core.pdb[nid]["mode"]
            prefix = mode if mode in ("html", "image") else "plain"
        except KeyError:
            prefix = "image" if path.suffix == ".png" else "plain"

        favorites = self.core.ndb["favorites"]
        suffix = "starred" if nid in favorites else "regular"
        icon = f"{prefix}_{suffix}"
        return self.core.icons[icon]

    def indexate(self):
        """ Creates and inserts folders menus, notes and sub-notes """
        fs_map = self._walk()
        self.browser = BrowserMenusData()
        self.central = CentralMenuData()
        self._build(fs_map)

    def _build(self, obj: dict, dest: SubMenu = None):
        """ Converts filesystem map to nested QMenus """
        folders = [obj[key] for key in obj if isinstance(obj[key], dict)]
        for f in folders:
            item = SubMenu(self.core, f["__path__"])
            if dest:
                self.browser.subfolders.setdefault(dest, [])
                self.browser.subfolders[dest].append(item)
            else:
                self.browser.folders.append(item)
            self._build(obj=f, dest=item)

        files = [obj[key] for key in obj if self._isFilePath(obj[key])]
        for f in files:
            if self._hasParents(f):
                item = SubAction(self.core, f)
                if f in self.core.loaded:
                    clone = LocalAction(self.core, f, prefix=True)
                    self.central.subnotes.append(clone)
                self.browser.subnotes.setdefault(dest, [])
                self.browser.subnotes[dest].append(item)
            else:
                item = LocalAction(self.core, f)
                self.central.notes.append(item)

    def _hasParents(self, path: Path):
        """ Verifies if a note is at the root of the notes directory """
        return self._parents(path)[:-1]

    def _insertSubActions(self):
        """ Sorts and inserts sub-actions and sub-notes actions """
        for obj, items in self.browser.subnotes.items():  # Insert nested notes
            items = self._sort(items)
            obj.addActions(items)

            for i in items:  # Insert custom folder actions (bottom)
                path = i.path.parent
                for key in self.core.sdb["core menus"]["browser"]:
                    if key == "separator":
                        obj.addSeparator()
                    else:
                        action = self.core.actions.browser[key]
                        self.browser.subactions.append(CoreAction(action, path))
                        obj.addAction(self.browser.subactions[-1])
                break

    def _insertSubMenus(self):
        """ Sorts and inserts sub-folders menus """
        for obj, items in self.browser.subfolders.items():
            items = self._sort(items)
            for i in items:
                obj.addMenu(i)

    def _isFilePath(self, obj: any) -> bool:
        """ Verifies if an object is a file Path """
        return isinstance(obj, Path) and obj.is_file()

    def _noneAction(self) -> QtWidgets.QWidgetAction:
        """ Returns a non interactive item when ConfigDirs.NOTES is empty """
        label = QtWidgets.QLabel("Note folder is empty")
        label.setAlignment(QtCore.Qt.AlignCenter)
        font = label.font()
        font.setItalic(True)
        label.setFont(font)
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(label)
        return action

    def _parents(self, path: Path) -> Tuple[str]:
        """ Returns a tuple of parent(s) folder(s) relative to the notes directory"""
        parents = path.relative_to(ConfigDirs.NOTES)
        return parents.parts

    def _refresh(self):
        """ Updates core menu on request """
        self.clear()
        self.indexate()
        for key in self.core.sdb["core menus"]["tray"]:
            if key == "separator":
                self.addSeparator()
            elif key == "folders list":
                self.addFoldersList()
            elif key == "notes list":
                self.addNotesList()
            else:
                action = self.core.actions.tray[key]
                self.central.items.append(CoreAction(action))
                self.addAction(self.central.items[-1])

    def _sort(self, data: list):
        """ Sorts a list of QMenus or QActions """
        try:
            return sorted(data, key=lambda item: item.title().lower())
        except AttributeError:
            return sorted(data, key=lambda item: item.text().lower())

    def _walk(self) -> dict:
        """ Maps content of notes directory recursively """
        struct = {}
        dirs = [x for x in ConfigDirs.NOTES.rglob("*") if x.is_dir()]
        for path in dirs:
            folders = self._parents(path)
            last = struct
            for f in folders:
                last.setdefault(f, {"__path__": path})
                last = last[f]

        for path in self.core.getNotesFiles(ConfigDirs.NOTES):
            folders = self._parents(path)[:-1]
            last = struct
            for f in folders:
                last = last[f]
            last[path.name] = path
        return struct


class CoreAction(QtWidgets.QAction):
    def __init__(self, action: Tuples.Action, path: Path = None):
        super().__init__()
        self.path = path
        self.action = action
        self.setIcon(action.icon)
        self.setText(action.label)
        self.triggered.connect(self._triggered)

    def _triggered(self):
        """ Handler for left click event, calls an action """
        if self.path:
            log.info(f"Core : {self.action.label} : {self.path}")
            self.action.call(self.path)
        else:
            log.info(f"Core : {self.action.label}")
            self.action.call()


class NoteAction(QtWidgets.QAction):
    def __init__(self, core, path: Path):
        super().__init__()
        self.core = core
        self.path = path
        self.setCheckable(True)
        self.triggered.connect(self._triggered)
        label = self._truncate(self.path.stem)
        self.setText(label)

    def _truncate(self, label: str) -> str:
        """ Truncates strings longer than a threshold value """
        threshold = self.core.sdb["general"]["truncate threshold"]
        if len(label) > threshold:
            label = f"{label[:threshold]} ..."
        return label


class LocalAction(NoteAction):
    def __init__(self, core, path: Path, prefix=False):
        super().__init__(core, path)
        if self.path in self.core.loaded:
            isVisible = self.core.loaded[path].isVisible()
            self.setChecked(isVisible)

        if prefix:
            db = ConfigDirs.NOTES
            parents = self.path.relative_to(db).parts[:-1]
            parents = " / ".join(parents)
            self.setText(f"{parents} / {self.text()}")

    def _triggered(self):
        """ Handler for left click event, toggles a note """
        self.core.notes.toggle(self.path)


class SubAction(NoteAction):
    def __init__(self, core, path: Path):
        super().__init__(core, path)
        self.setChecked(self.path in self.core.loaded)

    def _triggered(self):
        """ Handler for left click event, toggles a sub-note """
        if self.path in self.core.loaded:
            self.core.notes.close(self.path)
        else:
            self.core.notes.add(self.path)


class MoveDialog(QtWidgets.QFileDialog):
    """ Self-contained class for the folder move dialog (all modes) """
    def __init__(self, name: str):
        super().__init__()
        self.setDirectory(str(ConfigDirs.NOTES))
        self.setWindowTitle(f"Select a folder for '{name}'")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFileMode(QtWidgets.QFileDialog.Directory)
        self.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog | QtWidgets.QFileDialog.ShowDirsOnly)
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setViewMode(QtWidgets.QFileDialog.Detail)
        self.setModal(True)
        self.directoryEntered.connect(self._entered)
        self.Customize(self)

    def _backOrForwardClicked(self):
        """ Fix for missing Qt signals for back and forward buttons """
        path = self.directory().absolutePath()
        self.directoryEntered.emit(path)

    def _entered(self, current: str):
        """ Prevents navigation outside of notes root directory """
        if ConfigDirs.NOTES not in Path(current).parents:
            self.setDirectory(str(ConfigDirs.NOTES))

    class Customize:
        def __init__(self, dialog):
            self._disableComboBox(dialog)
            for child in (self._fixSignals, self._hideSidePanel, self._treeView):
                try:
                    child(dialog)
                except AttributeError:
                    pass

        def _disableComboBox(self, dialog):
            """ Disables navigation and filetype combo boxes """
            for comboBox in dialog.findChildren(QtWidgets.QComboBox):
                comboBox.setEnabled(False)

        def _fixSignals(self, dialog):
            """ Fix for missing Qt signals for back and forward buttons """
            back = dialog.findChild(QtWidgets.QToolButton, "backButton")
            forward = dialog.findChild(QtWidgets.QToolButton, "forwardButton")
            back.clicked.connect(dialog._backOrForwardClicked)
            forward.clicked.connect(dialog._backOrForwardClicked)

        def _hideSidePanel(self, dialog):
            """ Hides the left shortcut panel """
            listView = dialog.findChild(QtWidgets.QListView)
            listView.hide()

        def _treeView(self, dialog):
            """ Customizes tree view """
            treeView = dialog.findChild(QtWidgets.QTreeView)
            treeView.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # Name
            treeView.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)  # Date
            treeView.hideColumn(1)  # Size
            treeView.hideColumn(2)  # Type
