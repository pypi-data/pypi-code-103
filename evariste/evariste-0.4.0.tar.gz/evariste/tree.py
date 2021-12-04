# Copyright Louis Paternault 2016-2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Directory representation and compilation."""

from concurrent.futures import ThreadPoolExecutor
import functools
import itertools
import logging
import os
import pathlib
import shlex
import tarfile
import traceback

from evariste import plugins, utils, errors
from evariste.plugins.action import DirectoryAction
from evariste.hooks import methodhook

LOGGER = logging.getLogger(__name__)


def get_tree_plugins(self, *args, **kwargs):
    """Given the argument of :method:`Tree.__init__`, return a :class:`PluginLoader` instance."""
    # pylint: disable=unused-argument
    if isinstance(self, Root):
        root = self
    else:
        root = kwargs["parent"]
        while root.parent is not None:
            root = root.parent
    return root.shared.builder.plugins


@functools.total_ordering
class Tree:
    """Directory tree"""

    # pylint: disable=too-many-instance-attributes

    @methodhook(getter=get_tree_plugins)
    def __init__(self, path, *, parent):
        self._subpath = {}
        self.report = None
        self.parent = parent
        self.config = None
        if parent is not None:
            self.basename = pathlib.Path(path)
            self.from_fs = parent.from_fs / self.basename
            self.from_source = parent.from_source / self.basename
            self.vcs = self.parent.vcs
            self.shared = self.parent.shared
        self.local = self.shared.get_tree_view(path)

    def __hash__(self):
        return hash((hash(self.parent), self.from_fs))

    @property
    def relativename(self):
        """Return a 'relative' path.

        * For root, return path relative to file system (or directory of setup file).
        * For non-root, return path relative to parent (i.e. basename of path).
        """
        if isinstance(self, Root):
            return self.from_fs
        return self.basename

    @staticmethod
    def is_root():
        """Return ``True`` iff ``self`` is the root."""
        return False

    @property
    def depth(self):
        """Return the depth of the path.

        The root has depth 0, and depth of each path is one more than the depth
        of its parent.
        """
        if isinstance(self, Root):
            return 0
        return 1 + self.parent.depth

    @property
    def root(self):
        """Return the root of the tree."""
        if self.is_root():
            return self
        return self.parent.root

    def find(self, path):
        """Return the tree object corresponding to ``path`` if it exists; False otherwise.

        Argument can be:
        - a string (:type:`str`);
        - a :type:`pathlib.Path` object;
        - a tuple of strings, as a list of directories and (optional) final file.
        """
        if isinstance(path, str):
            pathtuple = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            pathtuple = path.parts
        else:
            pathtuple = path

        if not pathtuple:
            return self
        if pathtuple[0] in self:
            return self[pathtuple[0]].find(pathtuple[1:])
        return False

    def add_subpath(self, sub):
        """Add a subpath"""
        if len(sub.parts) > 1:
            self[sub.parts[0]].add_subpath(pathlib.Path(*sub.parts[1:]))
        else:
            self[sub.parts[0]]  # pylint: disable=pointless-statement

    def __iter__(self):
        return iter(self._subpath)

    def keys(self):
        """Iterator over subpaths (as :class:`str` objects)."""
        yield from self._subpath.keys()

    def values(self):
        """Iterator over subpaths (as :class:`Tree` objects)."""
        yield from self._subpath.values()

    def __contains__(self, key):
        return key in self._subpath

    def __getitem__(self, key):
        if key not in self:
            if (self.from_fs / key).is_dir():
                path_type = Directory
            else:
                path_type = File
            self._subpath[key] = path_type(key, parent=self)
        return self._subpath[key]

    def __delitem__(self, item):
        pathitem = pathlib.Path(item)
        if len(pathitem.parts) != 1:
            raise errors.EvaristeBug(
                "Argument '{}' should be a single directory or file, "
                "not a 'directory/directory' or directory/file'."
            )
        if str(pathitem) in self:
            del self._subpath[str(pathitem)]
            if (not self._subpath) and self.is_dir() and self.parent is not None:
                del self.parent[self.basename]

    def __str__(self):
        return self.from_fs.as_posix()

    def __len__(self):
        return len(self._subpath)

    def __eq__(self, other):
        return self.from_source == other.from_source

    def __lt__(self, other):
        if isinstance(self, Directory) and not isinstance(other, Directory):
            return True
        if not isinstance(self, Directory) and isinstance(other, Directory):
            return False
        return self.from_source < other.from_source

    def is_dir(self):
        """Return `True` iff `self` is a directory."""
        return issubclass(self.__class__, Directory)

    def is_file(self):
        """Return `True` iff `self` is a file."""
        return issubclass(self.__class__, File)

    def walk(self, dirs=False, files=True):
        """Iterator over files or directories  of `self`.

        :param bool dirs: If `False`, do not yield directories.
        :param bool files: If `False`, do not yield files.

        Directories are yielded *before* subfiles and subdirectories.
        """
        if (dirs and self.is_dir()) or (files and self.is_file()):
            yield self
        for sub in sorted(self):
            yield from self[sub].walk(dirs, files)

    def count(self, dirs=False, files=True):
        """Count the number of files or directories in this tree."""
        return sum(1 for _ in self.walk(dirs, files))

    def prune(self, path):
        """Remove a file.

        Argument can be either:
        - a :class:`pathlib.Path`,
        - a :class:`tuple`,
        - or a :class:`str` (which would be converted to a :class:`pathlib.Path`.

        If called with a non-existing path, does nothing.
        """
        if isinstance(path, str):
            path = pathlib.Path(path)
        if isinstance(path, tuple):
            parts = path
        elif isinstance(path, pathlib.Path):
            parts = path.parts
        else:
            raise TypeError

        # Does path exist?
        if parts[0] not in self:
            return

        # Remove (existing) path
        if len(parts) == 1:
            del self[parts[0]]
        else:
            self[parts[0]].prune(parts[1:])

    def format(self, string):
        """Format given string, with several variables related to ``self``."""
        suffix = self.from_source.suffix
        if suffix.startswith("."):
            suffix = suffix[1:]
        return string.format(
            dirname=self.parent.from_fs.as_posix(),
            filename=self.basename,
            fullname=self.from_fs.as_posix(),
            extension=suffix,
            basename=self.basename.stem,
        )

    def iter_readmes(self, renderers):
        """Iterate over readme files."""
        for renderer in renderers:
            for filename in renderer.iter_readme(self.from_fs, directory=self.is_dir()):
                yield pathlib.Path(filename).relative_to(self.root.from_fs)
                return

    def full_depends(self):
        """Return the list of all dependencies of this tree (recursively for directories)."""
        raise NotImplementedError()


class Directory(Tree):
    """Directory"""

    def prune_ignored(self):
        """Prune ignored files."""
        ignorename = self.from_fs / ".evsignore"
        if not ignorename.exists():
            return

        self.prune(".evsignore")

        with open(ignorename, encoding="utf8") as file:
            for line in file.readlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                try:
                    # Fake glob, to catch lines with invalid syntax.
                    for _ in self.from_fs.glob(line):
                        break
                except ValueError as error:
                    LOGGER.warning(
                        f"Line '{line}' has been ignored in file '{ignorename}': {error}."
                    )
                    continue
                for filename in self.from_fs.glob(line):
                    self.prune(filename.relative_to(self.from_fs))

    def compile(self):
        """Compile directory."""
        self.report = DirectoryAction(self.shared).compile(self)

    def iter_readmes(self, renderers):
        renderers = list(renderers)
        yield from super().iter_readmes(renderers)

        for sub in self:
            yield from self[sub].iter_readmes(renderers)

    def full_depends(self):
        for sub in self:
            yield from self[sub].full_depends()


class File(Tree):
    """File"""

    def prune_ignored(self):
        """Prune ignored files"""
        for name in ["{}.evsignore", ".{}.evsignore"]:
            if (self.parent.from_fs / name.format(self.basename)).exists():
                self.parent.prune(name.format(self.basename))
                self.parent.prune(self.basename)

    @methodhook()
    def compile(self):
        """Compile file."""
        # pylint: disable=too-many-branches

        # Find a plugin to compile the file
        # pylint: disable=unsubscriptable-object
        try:
            if not self.shared.builder.plugins.get_plugin("changed").compile(self):
                # Nothing has changed: it is useless to compile this again.
                compiler = self.shared.builder.plugins.get_plugin("action.cached")
            elif self.config["action"]["plugin"] is not None:
                compiler = self.shared.builder.plugins.get_plugin(
                    f"""action.{self.config["action"]["plugin"]}"""
                )
            else:
                compiler = self.shared.builder.plugins.match("action", self)
        except plugins.NoMatch:
            compiler = self.shared.builder.plugins.get_plugin("action.noplugin")

        # Actual compilation
        try:
            self.report = compiler.compile(self)
        except Exception as error:  # pylint: disable=broad-except
            if isinstance(error, errors.EvaristeError):
                message = str(error)
            else:
                message = "Error: Evariste internal error\n\n" + traceback.format_exc()
            LOGGER.error(message)
            self.report = plugins.action.Report(
                self,
                success=False,
                log=message,
            )

        # Add (optional) dependencies to the file
        # pylint: disable=unsubscriptable-object
        for regexp in itertools.chain(
            shlex.split(self.config[compiler.keyword].get("depends", "")),
            shlex.split(self.config["action"].get("depends", "")),
        ):
            for name in self.parent.from_fs.glob(regexp):
                if name.resolve() != self.from_fs.resolve():
                    if self.vcs.is_versionned(name):
                        self.report.depends.add(name)

    def iter_depends(self):
        """Iterate over dependencies."""
        for path in self.report.depends:
            yield path.resolve().relative_to(self.root.from_fs.resolve())

    @methodhook()
    def make_archive(self, destdir):
        """Make an archive of ``self`` and its dependency.

        Stes are:
        - build the archive;
        - copy it to ``destdir``;
        - return the path of the archive, relative to ``destdir``.

        If ``self`` has no dependencies, consider the file as an archive.

        It can be called several times: the archive will be built only once.
        """

        def common_root(files):
            """Look for the common root of files given in argument.

            Returns a tuple of `(root, relative_files)`, where
            `relative_files` is a list of `files`, relative to the root.
            """
            files = [
                file.resolve()
                for file in files
                if file.resolve()
                .as_posix()
                .startswith(self.root.from_fs.resolve().as_posix())
            ]
            root = pathlib.Path()
            while True:
                prefixes = [path.parts[0] for path in files]
                if len(set(prefixes)) != 1:
                    break
                prefix = prefixes[0]
                files = [file.relative_to(prefix) for file in files]
                root /= prefix
            return root.relative_to(self.root.from_fs.resolve()), files

        if (
            # Compilation was successful
            self.report.success
            # File has not been compiled again
            and not self.shared.builder.plugins.get_plugin("changed").compile(self)
            # Archive has already been generated
            and "archivepath" in self.shared.tree[self.from_source]["changed"]
        ):
            return self.shared.tree[self.from_source]["changed"]["archivepath"]

        if len(self.report.full_depends) == 1:
            utils.copy(self.from_fs.as_posix(), (destdir / self.from_source).as_posix())
            return self.from_source
        archivepath = self.from_source.with_suffix(f"{self.from_source.suffix}.tar.gz")
        os.makedirs(os.path.dirname((destdir / archivepath).as_posix()), exist_ok=True)

        archive_root, full_depends = common_root(self.report.full_depends)
        with tarfile.open((destdir / archivepath).as_posix(), mode="w:gz") as archive:
            for file in full_depends:
                archive.add(
                    (self.root.from_fs / archive_root / file).as_posix(),
                    file.as_posix(),
                )
        return archivepath

    def last_modified(self):
        """Return the last modified date and time of ``self``."""
        return self.vcs.last_modified(self.from_fs)

    def full_depends(self):
        yield from self.report.full_depends

    def depends(self):
        """Iterator over dependencies of this file (but not the file itself)."""
        yield from self.report.depends


class Root(Directory):
    """Root object (directory with no parents).

    Note that before calling :method:`Root.root_compile`,
    one must call :method:`Root.finalize`
    (it prune trees of ignored files, match files with their configuration…).
    This is automatically done if this object is created as a context manager, at when exiting it::

        with Root("foo") as root:
            root.add_subpath("bar")
        root.root_compile()

    This is also automatically done when object is created using factory :method:`Root.from_vcs`.
    """

    def __init__(self, path, *, vcs=None, shared=None):
        self.vcs = vcs
        self.shared = shared
        self.from_fs = path
        self.from_source = pathlib.Path(".")
        self.basename = pathlib.Path(".")
        self._finalized = False
        super().__init__(path, parent=None)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.finalize()

    def finalize(self):
        """Remove ignored files, and compute configuration."""
        # Remove ignored files
        for tree in list(self.walk(dirs=True, files=True)):
            tree.prune_ignored()

        # Set and remove configuration files
        self.set_config()

        self._finalized = True

    def _find_config(self):
        # Finding (potential) configuration files for directories
        for tree in self.walk(dirs=True, files=False):
            config = tree.from_fs / ".evsconfig"
            if config.exists():
                yield tree.from_source, config, utils.read_config(
                    config, allow_no_value=True
                )

        # Finding (potential) configuration files for files
        for tree in self.walk(dirs=False, files=True):
            for config in [".{}.evsconfig", "{}.evsconfig"]:
                config = tree.parent.from_fs / config.format(tree.basename)
                if config.exists():
                    yield tree.from_source, config, utils.read_config(
                        config, allow_no_value=True
                    )

    def set_config(self):
        """Compute the configuration of each file of the thee.

        That is:
        look for the file that configure it
        (typically `foo.evsconfig` is the configuration for file `foo`),
        load it,
        and complete it using the recursive configuration of parent directories.
        """
        recursive = {}

        # Assign configuration to files
        for tree, configname, config in list(self._find_config()):
            if utils.yesno(config.get("setup", "recursive", fallback=False)):
                recursive[tree] = config
                self.prune(configname.relative_to(self.from_fs))
                continue

            if config.get("setup", "source", fallback=False):
                if tree.is_dir():
                    tree = tree / config["setup"]["source"]
                else:
                    tree = tree.parent / config["setup"]["source"]

            tree = self.find(tree)
            if tree.config is not None:
                LOGGER.warning(  # pylint: disable=logging-fstring-interpolation
                    f"""Configuration file "{configname}" has been ignored for "{tree.from_fs}": another configuration file already applies."""  # pylint: disable=line-too-long
                )
                continue

            self.prune(configname.relative_to(self.from_fs))
            tree.config = utils.DeepDict.from_configparser(config)

        # Propagate recursive configuration from directories
        for directory, config in sorted(recursive.items(), reverse=True):
            for tree in self.find(directory).walk(dirs=True, files=True):
                if tree.config is None:
                    tree.config = utils.DeepDict.from_configparser(config)
                else:
                    tree.config.fill_blanks(config)

        # Set a default (empty) configuration to trees without any.
        for tree in self.walk(dirs=True, files=True):
            if tree.config is None:
                tree.config = utils.DeepDict(2)

    @staticmethod
    def is_root():
        return True

    def root_compile(self):
        """Recursively compile files.."""
        if not self._finalized:
            raise Exception(
                "You must call method `finalize()` before calling `root_compile()`."
            )

        # Compile files
        with ThreadPoolExecutor(
            max_workers=self.shared.setup["arguments"]["jobs"]
        ) as pool:
            for path in self.walk(dirs=False, files=True):
                pool.submit(path.compile)

        # Remove files that were not compiled (no plugin found to compile them)
        for path in self.walk(dirs=False, files=True):
            if path.report is None:
                self.prune(path.from_source)

        # Remove dependencies
        for path in list(self.walk(dirs=False, files=True)):
            if not self.find(path.from_source):
                # `path` may have been removed during the loop
                continue
            for file in path.iter_depends():
                self.prune(file)

        # "Compile" directories
        for path in reversed(list(self.walk(dirs=True, files=False))):
            path.compile()

    @classmethod
    def from_vcs(cls, repository):
        """Return a directory, fully set."""
        with cls(repository.source, vcs=repository, shared=repository.shared) as tree:
            for path in repository.walk():
                tree.add_subpath(pathlib.Path(path))
            return tree
