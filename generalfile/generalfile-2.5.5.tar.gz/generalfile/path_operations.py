
from generallibrary import deco_cache
from generalfile.errors import CaseSensitivityError
from generalfile.decorators import deco_require_state, deco_preserve_working_dir, deco_return_if_removed

import pathlib
import appdirs
import os
import shutil
from send2trash import send2trash
import json
from distutils.dir_util import copy_tree
import time

from generalfile.optional_dependencies._extension import WriteContext, ReadContext


class Path_Operations:
    """ File operations methods for Path. """
    _suffixIO = {"plain_text": ("txt", "md", ""), "spreadsheet": ("tsv", "csv")}
    timeout_seconds = 5
    dead_lock_seconds = 3
    _working_dir = None

    def _removed_path(self):
        """ :param generalfile.Path self: """
        self.set_parent(None)

    def open_operation(self, mode, func, encoding=..., no_file_default=...):
        """ Handles all open() calls.

            :param generalfile.Path self:
            :param mode:
            :param func:
            :param encoding:
            :param no_file_default: """
        if encoding is Ellipsis:
            encoding = "utf-8"

        try:
            with open(self, mode, encoding=encoding) as stream:
                return func(stream)
        except FileNotFoundError as e:
            if no_file_default is ...:
                raise e
            else:
                return no_file_default

    def write(self, content=None, overwrite=False, indent=None):
        """ Write to this Path with JSON.

            :param generalfile.Path self:
            :param any content: Serializable by JSON
            :param overwrite: Whether to allow overwriting or not.
            :param indent: """
        content_json = "" if content is None else json.dumps(content, indent=indent)
        with WriteContext(self, overwrite=overwrite) as write_path:
            write_path.open_operation("w", lambda stream: stream.write(content_json))
        return content_json

    def read(self, default=...):
        """ Read this Path with JSON.

            :param generalfile.Path self:
            :param default: Optionally return a default value. """
        with ReadContext(self) as read_path:
            return read_path.open_operation("r", lambda stream: json.loads(stream.read()), no_file_default=default)

    @deco_require_state(exists=True)
    def rename(self, name=None, stem=None, suffix=None, overwrite=False):
        """ Rename this single file or folder to anything.

            :param generalfile.Path self:
            :param name:
            :param stem:
            :param suffix:
            :param overwrite: """
        new_path = self
        for key, value in {"stem": stem, "suffix": suffix, "name": name}.items():
            if value is not None:
                new_path = getattr(new_path, f"with_{key}")(value)
        if new_path == self:
            return

        with self.lock(new_path):
            if overwrite:
                self._path.replace(new_path)
            else:
                self._path.rename(new_path)
            self._removed_path()
        return new_path

    @deco_require_state(exists=True)
    def copy(self, new_path, overwrite=False):
        """ Copy a file or folder next to itself with a new name.
        If target exists then it is removed first, so it cannot add to existing folders, use `copy_to_folder` for that.

        :param generalfile.Path self:
        :param generalfile.Path or str new_path:
        :param overwrite:
        :return:
        """
        new_path = self.with_name(self.Path(new_path).name())

        with self.lock(new_path):
            if new_path.exists():
                if overwrite:
                    new_path.delete()
                else:
                    raise AttributeError(f"Target path '{new_path}' exists but overwrite is `False`.")
            self._copy_file_or_folder(new_path=new_path)

    def _copy_file_or_folder(self, new_path):
        """ :param generalfile.Path self: """
        if self.is_file():
            shutil.copy(self.path, new_path, follow_symlinks=False)  # Can clobber
        else:
            copy_tree(self.path, new_path.path)

    @deco_require_state(exists=True)
    def _copy_or_move(self, target_folder_path, overwrite, method):
        """ :param generalfile.Path self: """
        target_folder_path = self.Path(target_folder_path)
        if target_folder_path.is_file():
            raise NotADirectoryError("parent_path cannot be a file")

        self_parent_path = self.absolute().get_parent() if self.is_file() else self.absolute()
        if self_parent_path == target_folder_path:
            return

        if self.is_file():
            filepaths = [self]
        else:
            filepaths = self.get_children()

        target_filepaths = [target_folder_path / path.absolute().relative(self_parent_path) for path in filepaths]
        if not overwrite and any([target.exists() for target in target_filepaths]):
            raise FileExistsError("Atleast one target filepath exists, cannot copy")

        with self.lock(target_folder_path):
            target_folder_path.create_folder()
            for path, target in zip(filepaths, target_filepaths):

                if method == "copy":
                    self.__class__._copy_file_or_folder(path, target)  # Same as path._copy_file_or_folder(target)

                elif method == "move":
                    shutil.move(path, target)  # Can clobber if full target path is specified like we do

            if method == "move":
                self._removed_path()
                if self.is_folder():
                    self.delete()

    def copy_to_folder(self, target_folder_path, overwrite=False):
        """ Copy file or files inside given folder to anything except it's own parent, use `copy` for that.

            :param generalfile.Path self:
            :param target_folder_path:
            :param overwrite: """
        return self._copy_or_move(target_folder_path=target_folder_path, overwrite=overwrite, method="copy")

    def move(self, target_folder_path, overwrite=False):
        """ Move files inside given folder or file to anything except it's own parent.

            :param generalfile.Path self:
            :param target_folder_path:
            :param overwrite: """
        return self._copy_or_move(target_folder_path=target_folder_path, overwrite=overwrite, method="move")

    def is_file(self):
        """ Get whether this Path is a file.

            :param generalfile.Path self: """
        return self._path.is_file()

    def is_folder(self):
        """ Get whether this Path is a folder.

            :param generalfile.Path self: """
        return self._path.is_dir()

    def is_root(self):
        """ Get whether this Path is a root.

            :param generalfile.Path self: """
        if self.verInfo.pathRootIsDelimiter:
            return self.path == self.path_delimiter
        else:
            return len(self.path) == 3 and self.path[1] == ":" and self.path[2] == self.path_delimiter

    def _case_sens_test(self, path):
        """ :param generalfile.Path self: """
        return self != path and self.path.lower() == str(path).lower()

    def exists(self):
        """ Get whether this Path exists.

            :param generalfile.Path self: """
        if self.get_sibling(spawn=False, filt=self._case_sens_test, traverse_excluded=True):
            raise CaseSensitivityError(f"Same path with differing case not allowed: '{self}'")
        return self._path.exists()

    def empty(self):
        """ Get whether path is an empty folder or not.

            :param generalfile.Path self: """
        if not self.exists():
            return True
        elif self.is_file():
            return False
        if self.get_child():
            return False
        return True

    def without_file(self):
        """ Get this path without it's name if it's a file, otherwise it returns itself.

            :param generalfile.Path self: """
        if self.is_file():
            return self.get_parent()
        else:
            return self

    def create_folder(self):
        """ Create folder with this Path unless it exists. 

            :param generalfile.Path self: """
        if self.exists():
            return False
        else:
            self._path.mkdir(parents=True, exist_ok=True)
            return True

    def open_folder(self):
        """ Open folder to view it manually.

            :param generalfile.Path self: """
        self.create_folder()
        os.startfile(self.without_file())

    @classmethod
    def get_working_dir(cls):
        """ Get current working folder as a new Path.
            Falls back to last seen working_dir if it doesn't exist. (Only seems to raise Error on posix)

            :param generalfile.Path cls:
            :rtype: generalfile.Path """
        # return cls.Path(pathlib.Path.cwd())

        try:
            working_dir = cls.Path(pathlib.Path.cwd())
        except FileNotFoundError as e:
            if cls._working_dir is None:
                raise e
            else:
                return cls._working_dir
        else:
            cls._working_dir = working_dir
            return working_dir

    def set_working_dir(self):
        """ Set current working folder.

            :param generalfile.Path self: """
        self.create_folder()
        self._working_dir = self.absolute()
        os.chdir(self._working_dir)

    @classmethod
    @deco_cache()
    def get_cache_dir(cls):
        """ Get cache folder.

            :param generalfile.Path or Any cls:
            :rtype: generalfile.Path """
        path = cls(appdirs.user_cache_dir())
        return path

    @classmethod
    @deco_cache()
    def get_lock_dir(cls):
        """ Get lock folder inside cache folder.

            :param generalfile.Path cls:
            :rtype: generalfile.Path """
        return cls.get_cache_dir() / "generalfile" / "locks"

    @deco_cache()
    def get_lock_path(self):
        """ Get absolute lock path pointing to actual lock.

            :param generalfile.Path self:
            :rtype: generalfile.Path """
        return self.get_lock_dir() / self.absolute().to_alternative()

    @deco_preserve_working_dir
    @deco_return_if_removed(content=False)
    def delete(self, error=True):
        """ Delete a file or folder.

            :param error:
            :param generalfile.Path self: """
        with self.lock():
            try:
                if self.is_file():
                    os.remove(self)
                elif self.is_folder():
                    shutil.rmtree(self)
            except PermissionError:
                self.trash()  # Sometimes failing to remove a git file on windows, send2trash still worked
            except Exception as e:
                if error:
                    raise e

            self._removed_path()

    @deco_preserve_working_dir
    @deco_return_if_removed(content=False)
    def trash(self):
        """ Trash a file or folder.

            :param generalfile.Path self: """
        with self.lock():
            send2trash(self.path)

            self._removed_path()

    @deco_preserve_working_dir
    @deco_return_if_removed(content=True)
    def delete_folder_content(self):
        """ Delete every path in a folder.

            :param generalfile.Path self: """
        for path in self.get_children(gen=True):
            path.delete()

    @deco_preserve_working_dir
    @deco_return_if_removed(content=True)
    def trash_folder_content(self):
        """ Trash a file or folder and then create an empty folder in it's place.

            :param generalfile.Path self: """
        for path in self.get_children(gen=True):
            path.trash()

    @deco_require_state(is_file=True)
    def seconds_since_creation(self):
        """ Get time in seconds since file was created.
            NOTE: Doesn't seem to update very quickly for windows (7).

            :param generalfile.Path self: """
        return time.time() - os.path.getctime(self)

    @deco_require_state(is_file=True)
    def seconds_since_modified(self):
        """ Get time in seconds since file was modified.

            :param generalfile.Path self: """
        return time.time() - os.path.getmtime(self)

    @deco_require_state(is_file=True)
    def size(self):
        """ Get size in bytes of file.

            :param generalfile.Path self: """
        return self._path.stat().st_size

    def is_identical(self, path):
        """ Get whether this file's content is identical to another.

            :param generalfile.Path self:
            :param path: """
        path = self.Path(path)
        self_exists = self.exists()
        path_exists = path.exists()

        if not self_exists or not path_exists:
            return self_exists == path_exists

        with self.lock(path):
            with open(self, "r") as file1:
                with open(path, "r") as file2:
                    return file1.read() == file2.read()

    @deco_require_state(is_folder=True)
    def get_differing_files(self, target, exist=True, content=True, filt=None):
        """ Get a set of changed files by comparing two folders.

            :param generalfile.Path self:
            :param target:
            :param exist: Whether to compare files' existence. Ignores content.
            :param content: Whether to compare files' content if both files exist.
            :param filt: Optional filter, takes one Path as arg. """
        target = self.Path(target)
        assert target.is_folder()

        if filt is None:
            new_filt = lambda path: path.is_file()
        else:
            new_filt = lambda path: path.is_file() and filt(path)

        self_paths = {child.relative(self) for child in self.get_children(depth=-1, filt=new_filt, traverse_excluded=True)}
        target_paths = {child.relative(target) for child in target.get_children(depth=-1, filt=new_filt, traverse_excluded=True)}

        diff = set()
        if exist:
            diff.update(self_paths.symmetric_difference(target_paths))
        if content:
            diff.update({path for path in self_paths.intersection(target_paths) if path not in diff and not (self / path).is_identical(path=target / path)})
        return diff

    @deco_require_state(is_file=True)
    def contains(self, text):
        """ Return whether text string exists in one of the lines in this file.

            :param generalfile.Path self:
            :param text: """
        with self.lock():
            with open(self, "r") as stream:
                for line in stream:
                    if text in line:
                        return True
        return False

    def _pack_default_suffix(self):
        """ :param generalfile.Path self: """
        if not self.suffix():
            return self.with_suffix(".zip")
        else:
            return self

    @deco_require_state(is_folder=True)
    def pack(self, target, overwrite=False):
        """ Pack self which is folder to a new target archive.

            :param generalfile.Path self: Base folder to be packed.
            :param target: Full path of new archive. Optional suffix, defaults to zip if missing.'
            :param overwrite: """
        target = self.Path(target)._pack_default_suffix().absolute()
        if not overwrite:
            assert not target.exists()

        root_dir = self.absolute()
        target_stem = str(target.with_suffixes())
        target_suffix = "".join(target.suffixes())[1:]
        target_suffix = {"tar.gz": "gztar"}.get(target_suffix, target_suffix)

        shutil.make_archive(root_dir=root_dir, base_name=target_stem, format=target_suffix)

        return target

    def unpack(self, base, overwrite=False):
        """ Unpack self which is archive to target folder (Must be empty if overwrite is False).

            :param generalfile.Path self:
            :param base:
            :param overwrite: """
        base = self.Path(base)
        if not overwrite:
            assert not base.exists() or base.empty()

        shutil.unpack_archive(filename=self._pack_default_suffix(), extract_dir=base)
        return base



















