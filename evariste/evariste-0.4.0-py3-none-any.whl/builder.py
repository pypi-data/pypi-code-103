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

"""Builder

Takes care of build process.
"""

import contextlib
import functools
import logging

from evariste import errors
from evariste import plugins
from evariste.cache import open_cache
from evariste.hooks import methodhook
from evariste.plugins import PluginLoader
from evariste.setup import Setup, SetupError
from evariste.tree import Root
import evariste

LOGGER = logging.getLogger(evariste.__name__)


class Builder(contextlib.AbstractContextManager):
    """Takes care of build process. Can be used as a context."""

    # pylint: disable=no-member

    def __init__(self, setup):
        self.cache = open_cache(setup["setup"]["cachedir"], setup, self)
        self.shared = self.cache.shared
        self.plugins = PluginLoader(shared=self.shared)

        LOGGER.info("Building directory tree…")
        try:
            vcs = list(self.plugins.iter_plugins(plugin_type="vcs"))
            if len(vcs) != 1:
                raise errors.EvaristeError(
                    # pylint: disable=consider-using-f-string
                    "Exactly one vcs plugin must be enabled (right now: {}).".format(
                        ", ".join([plugin.keyword for plugin in vcs])
                    )
                )
            with self.plugins.apply_context_hook("buildtree", self):
                self.tree = Root.from_vcs(vcs[0])
        except plugins.NoMatch as error:
            raise SetupError(
                # pylint: disable=consider-using-f-string
                "Setup error: Value '{}' is not a valid vcs (available ones are: {}).".format(
                    error.value,
                    ", ".join([f"'{item}'" for item in error.available]),
                )
            ) from error

    @methodhook()
    def compile(self):
        """Compile files handled by this builder."""
        LOGGER.info("Compiling…")
        self.tree.root_compile()
        self.prune_readmes()

    def prune_readmes(self):
        """Remove readme files from tree."""
        for plugin in self.plugins.get_plugin_type("renderer").values():
            plugin.prune_readmes(self.tree)

    @methodhook()
    def close(self):
        """Perform close operations."""
        self.cache.close()

    @classmethod
    def from_setupname(cls, name):
        """Factory that returns a builder, given the name of a setup file."""
        LOGGER.info("Reading setup…")
        return cls(Setup.from_file(name))

    @classmethod
    def from_setupdict(cls, dictionary):
        """Factory that returns a builder, given a setup dictionary."""
        LOGGER.info("Reading setup…")
        return cls(Setup(dictionary))

    def iter_renderers(self):
        """Iterator over renderers.

        Iterate over :func:`functools.partial` objects, over the renderers
        :meth:`render` method, with tree as the first argument. More arguments
        can be added when calling the partial object.
        """
        for renderer in self.plugins.iter_plugins("renderer"):
            LOGGER.info(f"Rendering {renderer.keyword}…")
            yield functools.partial(renderer.render, self.tree)

    def get_renderer(self, keyword):
        """Return the renderer of given keyword."""
        for renderer in self.plugins.iter_plugins("renderer"):
            if renderer.keyword == keyword:
                return renderer
        raise KeyError(f"No renderer named '{keyword}'.")

    def __enter__(self, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        return super().__enter__(*args, **kwargs)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()
        return super().__exit__(exc_type, exc_value, traceback)
