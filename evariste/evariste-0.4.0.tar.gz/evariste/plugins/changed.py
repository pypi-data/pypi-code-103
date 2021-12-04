# Copyright Louis Paternault 2015-2021
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

"""Plugin to evaluate and store modification times of files.

It is used not to re-compile files that have not changed.
"""

from datetime import datetime
import os
import pathlib

from evariste import hooks
from evariste import plugins
from evariste.tree import File


class MakeArchive(hooks.MethodHook):
    """Hook called before and after archive creation."""

    # pylint: disable=too-few-public-methods

    hookname = "File.make_archive"

    def wrap(self, function):
        """Return a wrapped version of `function`, caching return value."""

        def wrapped(tree, destdir):
            """Wrapped function."""
            # pylint: disable=unused-argument
            value = function(tree, destdir)
            if self.plugin.compile(tree):
                self.local.tree[tree.from_source]["archivepath"] = value
            return value

        return wrapped


class BuildTreeItem(hooks.ContextHook):
    """Hook called before and after the tree is built."""

    # pylint: disable=too-few-public-methods

    hookname = "Tree"

    def __init__(self, plugin, tree, path, parent):
        # pylint: disable=unused-argument
        super().__init__(plugin)
        self.tree = tree

    def __exit__(self, *args, **kwargs):
        """Compare data with cache to see if a compilation is needed."""
        if not isinstance(self.tree, File):
            return

        tree = self.tree

        # If the --always-compile argument was given to the command line call,
        # do compile.
        if self.shared.setup["arguments"]["always_compile"]:
            self.plugin.files_to_compile.add(tree.from_fs.resolve())
            return

        # If tree is not in hash, compile it
        if (self.local.tree[tree.from_source] is None) or (
            self.local.tree[tree.from_source] == {}
        ):
            self.plugin.files_to_compile.add(tree.from_fs.resolve())
            return

        # Otherwise, check if data hash has changed
        for key in ["depends", "targets"]:
            dependencies = self.local.tree[tree.from_source][key]
            for depend in dependencies:
                cache_mtime = dependencies[depend][self.local.setup["time"]]
                if self.local.setup["time"] == "vcs":
                    file_mtime = tree.vcs.last_modified(pathlib.Path(depend))
                else:
                    try:
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(depend))
                    except FileNotFoundError:
                        self.plugin.files_to_compile.add(tree.from_fs.resolve())
                        return
                if cache_mtime != file_mtime:
                    self.plugin.files_to_compile.add(tree.from_fs.resolve())
                    return


class CompileFile(hooks.ContextHook):
    """Hook called before and after compilation of one file."""

    # pylint: disable=too-few-public-methods

    hookname = "File.compile"

    def __init__(self, plugin, tree):
        super().__init__(plugin)
        self.tree = tree

    def __exit__(self, *args, **kwargs):
        """Store the modification time of file and its dependencies."""
        if not isinstance(self.tree, File):
            return

        tree = self.tree
        if not tree.report.success:
            self.plugin.files_to_compile.discard(tree.from_fs.resolve())
            return

        if self.local.tree[tree.from_source] is None:
            self.local.tree[tree.from_source] = {}

        # Saving file and dependencies data into cache
        self.local.tree[tree.from_source]["depends"] = {
            file.as_posix(): {
                "vcs": tree.vcs.last_modified(file),
                "fs": datetime.fromtimestamp(os.path.getmtime(file.as_posix())),
            }
            for file in tree.full_depends()
        }

        self.local.tree[tree.from_source]["targets"] = {}
        for target in tree.report.targets:
            targetpath = tree.root.from_fs / target
            self.local.tree[tree.from_source]["targets"][targetpath.as_posix()] = {
                "vcs": tree.vcs.last_modified(targetpath),
                "fs": datetime.fromtimestamp(os.path.getmtime(targetpath.as_posix())),
            }

        # Mark dependencies as ignored (not to be compiled)
        self.plugin.files_to_ignore.update(
            [depend.resolve() for depend in tree.depends()]
        )


class Changed(plugins.PluginBase):
    """Evaluate and store modification times of files."""

    plugin_type = ""
    keyword = "changed"
    default_setup = {"time": "vcs"}
    hooks = [BuildTreeItem, CompileFile, MakeArchive]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files_to_compile = set()
        self.files_to_ignore = set()

    def compile(self, tree):
        """Return `True` iff file `tree` is to be compiled.

        It is not compiled if:
        - nothing has changed since last compilation;
        - it is a dependency of a file described in previous item.
        """
        return (tree.from_fs.resolve() in self.files_to_compile) and (
            tree.from_fs.resolve() not in self.files_to_ignore
        )
