
import pathlib
import os


from generallibrary import VerInfo, TreeDiagram, Recycle, classproperty, deco_cache

from generalfile.errors import InvalidCharacterError
from generalfile.path_lock import Path_ContextManager
from generalfile.path_operations import Path_Operations
from generalfile.path_strings import Path_Strings
from generalfile.optional_dependencies.path_spreadsheet import Path_Spreadsheet
from generalfile.optional_dependencies.path_text import Path_Text
from generalfile.optional_dependencies.path_cfg import Path_Cfg
from generalfile.optional_dependencies.path_pickle import Path_Pickle


class Path(TreeDiagram, Recycle, Path_ContextManager, Path_Operations, Path_Strings, Path_Spreadsheet, Path_Text, Path_Cfg, Path_Pickle):
    """ Immutable cross-platform Path.
        Built on pathlib and TreeDiagram.
        Implements rules to ensure cross-platform compatability.
        Adds useful methods.
        Todo: Binary extension. """
    verInfo = VerInfo()
    _path_delimiter = verInfo.pathDelimiter
    Path = ...

    _recycle_keys = {"path": lambda path: Path.scrub("" if path is None else str(path))}
    _alternative_chars = {_path_delimiter: "&#47;", ":": "&#58", ".": "&#46;"}

    def __init__(self, path=None):  # Don't have parent here because of Recycle
        self.path = self.scrub(str_path="" if path is None else str(path))

        self._path = pathlib.Path(self.path)
        self._latest_listdir = set()

    copy_node = NotImplemented  # Maybe something like this to disable certain methods

    @classproperty
    def path_delimiter(cls):
        return cls._path_delimiter

    def spawn_parents(self):
        if not self.get_parent(spawn=False) and self.path and not self.is_root():
            try:
                index = self.path.rindex(self.path_delimiter) + 1
            except ValueError:
                index = 0
            self.set_parent(Path(path=self.path[:index]))

    def spawn_children(self):
        if self.is_folder():
            old_children = {path.name() for path in self.get_children(spawn=False)}

            try:
                new_children = set(os.listdir(self.path if self.path else "."))
            except PermissionError:
                new_children = set()

            for name in old_children.symmetric_difference(new_children):
                path = Path(path=self / name)
                path.set_parent(self if name in new_children else None)

    def __str__(self):
        return getattr(self, "path", "<Path not loaded yet>")
        # return self.path

    def __repr__(self):
        return self.name()

    def __fspath__(self):
        return self.path

    def __format__(self, format_spec):
        return self.path.__format__(format_spec)

    def __truediv__(self, other):
        """ :rtype: generalfile.Path """
        # print("here", self._recycle_instances)
        return self.Path(self._path / str(other))

    def __eq__(self, other):
        if isinstance(other, Path):
            other = other.path
        else:
            other = self._scrub("" if other is None else str(other))
        return self.path == other

    def __hash__(self):
        return hash(self.path)

    def __contains__(self, item):
        return self.path.__contains__(item)

    @classmethod
    def _scrub(cls, str_path):
        str_path = cls._replace_delimiters(str_path=str_path)
        str_path = cls._invalid_characters(str_path=str_path)
        str_path = cls._trim(str_path=str_path)
        str_path = cls._delimiter_suffix_if_root(str_path=str_path)
        return str_path

    @classmethod
    @deco_cache()
    def scrub(cls, str_path):
        return cls._scrub(str_path=str_path)

    @classmethod
    @deco_cache()
    def _replace_delimiters(cls, str_path):
        str_path = str_path.replace("/", cls.path_delimiter)
        str_path = str_path.replace("\\", cls.path_delimiter)
        return str_path

    @classmethod
    @deco_cache()
    def _invalid_characters(cls, str_path):
        # Simple invalid characters testing from Windows
        for character in '<>"|?*':
            if character in str_path:
                raise InvalidCharacterError(f"Invalid character '{character}' in '{str_path}'")

        if ":" in str_path:
            if not cls.verInfo.pathRootHasColon:
                raise InvalidCharacterError(f"Path has a colon but '{cls.verInfo.os}' doesn't use colon for path root: '{str_path}'")
            if str_path[1] != ":":
                raise InvalidCharacterError(f"Path has a colon but there's no colon at index 1: '{str_path}'")
            if len(str_path) >= 3 and str_path[2] != cls.path_delimiter:
                raise InvalidCharacterError(f"Path has a colon but index 2 is not a delimiter: '{str_path}'")
            if ":" in str_path[2:]:
                raise InvalidCharacterError(f"Path has a colon that's not at index 1: '{str_path}'")

        if str_path.endswith("."):
            raise InvalidCharacterError(f"Path cannot end with a dot ('.').")
        return str_path

    @classmethod
    @deco_cache()
    def _trim(cls, str_path):
        if not cls.verInfo.pathRootIsDelimiter and str_path.startswith(cls.path_delimiter):
            str_path = str_path[1:]
        if str_path.endswith(cls.path_delimiter) and len(str_path) > 1:
            str_path = str_path[0:-1]
        return str_path

    @classmethod
    @deco_cache()
    def _delimiter_suffix_if_root(cls, str_path):
        if len(str_path) == 2 and str_path[1] == ":":
            return f"{str_path}{cls.path_delimiter}"
        return str_path

setattr(Path, "Path", Path)














































