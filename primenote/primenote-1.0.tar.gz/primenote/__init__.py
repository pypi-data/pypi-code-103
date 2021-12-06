#!/usr/bin/python3
import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterator, Tuple
from PyQt5 import QtDBus

try:
    from .__id__ import ID, HELP
    from .backend import logger
    from .backend.cli import parser
    from .backend.constants import ConfigDirs, ConfigFiles, RootDirs, RootFiles
except ImportError:
    from __id__ import ID, HELP
    from backend import logger
    from backend.cli import parser
    from backend.constants import ConfigDirs, ConfigFiles, RootDirs, RootFiles

log = logger.new(__name__)


def initialize(args: argparse.Namespace):
    service = f"org.{ID}"
    path = f"/org/{ID}"
    bus = QtDBus.QDBusConnection.sessionBus()
    interface = QtDBus.QDBusInterface(service, path, "", bus)

    if interface.isValid():
        interface.call("ParseCommands", sys.argv[1:])  # FIXME: Can a Namespace object be sent through DBus ?
        sys.exit(0)
    else:
        Setup.install()
        if args.reset:
            Setup.reset(args.reset)
        try:
            app = __import__(f"{ID}.main", fromlist=["main"])
        except ImportError:
            import main as app
        app.main(args)


def main():
    args = parser(sys.argv[1:])  # Early filter for help or malformed commands
    if args.help:
        for h in HELP:
            print(h.expandtabs(18))
        sys.exit(0)
    initialize(args)


class Setup:
    @classmethod
    def install(cls):
        """ Initializes configuration files """
        with open(ConfigFiles.LOG, "w", encoding="utf-8"):
            log.info("Cleaned previous session log")
        cls._installDirs()
        cls._installFiles()

    @classmethod
    def reset(cls, args: str):
        """ Resets userspace configuration files """
        if args == "all":
            cls.reset("settings")
            cls.reset("profiles")
            cls.reset("css")
            cls.reset("vim")
            cls.reset("terminal")

        elif args == "settings":
            cls._deleteFiles((ConfigFiles.SETTINGS, ConfigFiles.NOTES))

        elif args == "profiles":
            cls._deleteFiles((ConfigFiles.PROFILES,))

        elif args == "terminal":
            paths = [group for group in cls._unfold(RootDirs.TERMINAL)]
            cls._resetFiles(paths)

        elif args == "css":
            paths = [(RootFiles.CSS, ConfigFiles.CSS)]
            paths += [group for group in cls._unfold(RootDirs.PALETTES)]
            paths += [group for group in cls._unfold(RootDirs.STYLES)]
            cls._resetFiles(paths)

        elif args == "vim":
            paths = [group for group in cls._unfold(RootDirs.VIM)]
            cls._resetFiles(paths)

    def _copyFile(src: Path, dest: Path):
        """ Copies a file and creates its parent tree """
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    @classmethod
    def _deleteFiles(cls, paths: Tuple[Path]):
        """ Removes a file without errors """
        for path in paths:
            try:
                path.unlink()
                log.warning(f"Removed user file '{cls._shortName(path)}'")
            except PermissionError:
                log.error(f"PermissionError: Could not delete '{cls._shortName(path)}'")
            except FileNotFoundError:
                log.error(f"FileNotFoundError: Could not delete '{cls._shortName(path)}'")

    @classmethod
    def _hasChanges(cls, root: Path, user: Path) -> bool:
        """ Verifies if two files are the same """
        with open(root, encoding="utf-8") as f1, open(user, encoding="utf-8") as f2:
            return f1.read() != f2.read()

    @classmethod
    def _installDirs(cls):
        """ Copies the configuration directories trees """
        ConfigDirs.NOTES.mkdir(parents=True, exist_ok=True)
        dirs = ((RootDirs.TERMINAL, ConfigDirs.TERMINAL),
                (RootDirs.PALETTES, ConfigDirs.PALETTES),
                (RootDirs.STYLES, ConfigDirs.STYLES),
                (RootDirs.VIM, ConfigDirs.VIM))

        for root, user in dirs:
            if not user.exists():
                shutil.copytree(root, user)
                log.info(f"Copied default directory '{cls._shortName(user)}'")

    @classmethod
    def _installFiles(cls):
        """ Copies the configuration files """
        files = ((RootFiles.CSS, ConfigFiles.CSS),
                 (RootFiles.VIM, ConfigFiles.VIM))

        for root, user in files:
            if not user.exists():
                cls._copyFile(root, user)
                log.info(f"Copied default file '{cls._shortName(user)}'")

    @classmethod
    def _overwrite(cls, root: Path, user: Path):
        """ Prompts user before overwriting existing configuration """
        log.warning(f"Resetting '{cls._shortName(user)}'")
        if cls._prompt(f"This will overwrite all changes made in '{user.name}'. Continue?"):
            cls._copyFile(root, user)
            log.warning(f"Overwritten user file '{cls._shortName(user)}'")

    def _prompt(question: str) -> bool:
        """ Command-line interface prompt for user confirmation """
        reply = None
        while reply not in ("", "y", "n"):
            reply = input(f"{question} (Y/n): ").lower()
        return (reply in ("", "y"))

    @classmethod
    def _resetFiles(cls, files: tuple):
        """ Copies non-existent configuration, else prompt user for overwriting """
        for root, user in files:
            if not user.exists():
                cls._copyFile(root, user)
                log.info(f"Copied default file '{cls._shortName(user)}'")
            elif cls._hasChanges(root, user):
                cls._overwrite(root, user)

    def _shortName(path: Path) -> str:
        """ Replaces path to home directory with ~ """
        return str(path).replace(str(Path.home()), "~")

    def _unfold(path: Path) -> Iterator[Tuple]:
        """ Returns all files contained in a folder """
        rootFiles = [f for f in path.rglob("*") if f.is_file()]
        for root in rootFiles:
            user = ConfigDirs.CFG / root.relative_to(RootDirs.ROOT)
            yield (root, user)


if __name__ == "__main__":
    main()
