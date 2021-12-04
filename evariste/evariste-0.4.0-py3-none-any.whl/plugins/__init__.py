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


"""Plugin loader"""

import collections
import contextlib
import functools
import logging
import os
import shlex
import sys

from evariste import errors, utils, setup
from evariste import hooks
import evariste

LOGGER = logging.getLogger(evariste.__name__)
DEFAULT_PLUGINS = {
    "action.cached",
    "action.directory",
    "action.noplugin",
    "action.raw",
    "changed",
    "logging",
}


class NoMatch(errors.EvaristeError):
    """No plugin found matching ``value``."""

    def __init__(self, value, available):
        super().__init__()
        self.value = value
        self.available = available

    def __str__(self):
        return f"Value '{self.value}' does not match any of {self.available}."


class SameKeyword(errors.EvaristeError):
    """Two plugins have the same keyword."""

    def __init__(self, keyword, plugin1, plugin2):
        super().__init__()
        self.keyword = keyword
        self.plugins = (plugin1, plugin2)

    def __str__(self):
        # pylint: disable=line-too-long
        return f"""Plugins '{self.plugins[0].__name__}' and '{self.plugins[1].__name__}' have the same keyword '{self.keyword}'."""


class NotAPlugin(errors.EvaristeError):
    """Superclass of plugins is not a plugin."""

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __str__(self):
        return (
            """Class '{obj.__module__}.{obj.__name__}' is not a plugin """
            """(it should inherit from """
            """'{superclass.__module__}.{superclass.__name__}')."""
        ).format(obj=self.obj, superclass=PluginBase)


class PluginNotFound(errors.EvaristeError):
    """Plugin cannot be found."""

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def __str__(self):
        return f"Cannot find plugin '{self.keyword}'."


@functools.total_ordering
class PluginBase:
    """Plugin base: all imported plugins must be subclasses of this class."""

    # pylint: disable=too-few-public-methods

    keyword = None
    priority = 0
    default_setup = {}
    global_default_setup = {}
    plugin_type = None
    hooks = []
    depends = {}

    def __init__(self, shared):
        self.shared = shared
        self.local = shared.get_plugin_view(self.keyword)
        self._set_default_setup()

    def _set_default_setup(self):
        """Set default value for this plugin setup, if necessary."""
        default = setup.Setup()
        for parent in reversed(self.__class__.mro()):  # pylint: disable=no-member
            if hasattr(parent, "default_setup"):
                default.update(parent.global_default_setup)
                default.update({self.keyword: parent.default_setup})
        self.shared.setup.fill_blanks(default)

    def match(self, value, *args, **kwargs):  # pylint: disable=unused-argument
        """Return ``True`` iff ``value`` matches ``self``.

        Default is keyword match. This method can be overloaded by
        subclasses.
        """
        return value == self.keyword

    def __lt__(self, other):
        priority = self.priority
        if callable(priority):
            priority = priority()  # pylint: disable=not-callable
        other_priority = other.priority
        if callable(other_priority):
            other_priority = other_priority()
        if priority == other_priority:
            return self.keyword < other.keyword
        return priority < other_priority


def find_plugins(libdirs=None):
    """Iterate over available plugins.

    :param list libdirs: Additional list of directories where plugins can be found.
    """
    if libdirs is None:
        libdirs = []

    path = []
    path.extend(
        [
            os.path.join(utils.expand_path(item), "plugins")
            for item in [".evariste", "~/.config/evariste", "~/.evariste"]
        ]
    )
    path.extend([utils.expand_path(item) for item in libdirs])
    path.extend([os.path.join(item, "evariste") for item in sys.path])

    yielded = set()
    for module in utils.iter_modules(path, "evariste.", LOGGER.debug):
        for attr in dir(module):
            if attr.startswith("_"):
                continue
            obj = getattr(module, attr)

            if isinstance(obj, type) and issubclass(obj, PluginBase):
                if obj.keyword is None:
                    continue
                if obj in yielded:
                    continue
                yielded.add(obj)
                yield obj


def find_plugins_sorted(libdirs=None):
    """Like :fun:`find_plugins`, but returns a :class:`utils.DeepDict`.

    The returned object is a dictionary of dictionaries:
    - first keys are plugin types;
    - second keys are plugin keywords;
    - values are the only plugin of said type and said keyword.
    """
    plugindict = utils.DeepDict(2)

    for plugin in find_plugins(libdirs):
        if plugin.keyword in plugindict[plugin.plugin_type]:
            raise SameKeyword(
                plugin.keyword,
                plugin,
                plugindict[plugin.plugin_type][plugin.keyword],
            )

        plugindict[plugin.plugin_type][plugin.keyword] = plugin
    return plugindict


def get_plugins(self, *_args, **_kwargs):
    """Given a :class:`PluginLoader` object, return itself.

    Useful to give hooks the plugins object.
    """
    return self


def get_libdirs(libdirs):
    """Convert `libdirs` setup option (as a string) to a list of path (as strings)."""
    if not libdirs:
        return []
    if isinstance(libdirs, str):
        return shlex.split(libdirs)
    if isinstance(libdirs, list):
        return libdirs
    return []


class PluginLoader:
    """Load plugins"""

    # pylint: disable=too-few-public-methods

    def __init__(self, *, shared):
        # pylint: disable=too-many-branches
        self.shared = shared

        # Load plugins:
        # Given the avaialble plugins, only loads relevant plugins.
        to_load = set()
        self.available = find_plugins_sorted(
            get_libdirs(self.shared.setup["setup"]["libdirs"])
        )

        # Step 0: Convert setup options in a list of keyword
        if self.shared.setup["setup"]["enable_plugins"] is None:
            self.shared.setup["setup"]["enable_plugins"] = []
        else:
            if isinstance(self.shared.setup["setup"]["enable_plugins"], str):
                self.shared.setup["setup"]["enable_plugins"] = shlex.split(
                    self.shared.setup["setup"]["enable_plugins"]
                )
            elif isinstance(self.shared.setup["setup"]["enable_plugins"], list):
                pass
            else:
                raise ValueError(
                    (
                        # pylint: disable=consider-using-f-string, line-too-long
                        "'Setup[setup][enable_plugins]' should be a string or a list (is now {}: '{}')."
                    ).format(
                        type(self.shared.setup["setup"]["enable_plugins"]),
                        self.shared.setup["setup"]["enable_plugins"],
                    )
                )

        # Step 1: Add enabled plugins
        for keyword in self.shared.setup["setup"]["enable_plugins"]:
            try:
                self.available.get_subkey(keyword)
            except KeyError as error:
                raise PluginNotFound(keyword) from error
            to_load.add(keyword)

        # Step 2: Enable/disable plugins according to their "enable" configuration
        for types in self.available.values():
            for plugin in types.values():
                if "enable" in self.shared.setup[plugin.keyword]:
                    if utils.yesno(self.shared.setup[plugin.keyword]["enable"]):
                        to_load.add(plugin.keyword)
                    else:
                        to_load.discard(plugin.keyword)

        # Step 3: Add default plugins
        to_load |= DEFAULT_PLUGINS

        # Step 4: Manage dependencies
        to_process = to_load.copy()
        processed = set()
        while to_process:
            keyword = to_process.pop()

            try:
                # Check if plugin exists
                self.available.get_subkey(keyword)
            except KeyError as error:
                raise PluginNotFound(keyword) from error

            for dependency in self.available.get_subkey(keyword).depends:
                try:
                    # Check if plugin exists
                    self.available.get_subkey(dependency)
                except KeyError as error:
                    raise PluginNotFound(dependency) from error
                if (dependency not in to_load) and (dependency not in processed):
                    to_load.add(dependency)
                    to_process.add(dependency)
            processed.add(keyword)

        # Step 5: Instanciate plugins
        self.plugins = collections.defaultdict(dict)
        for keyword in to_load:
            plugin = self.available.get_subkey(keyword)
            self.plugins[plugin.plugin_type][keyword] = plugin(self.shared)

    def iter_plugins(self, plugin_type=None):
        """Iterate over plugins."""
        if plugin_type is None:
            for ptype in self.plugins:
                for keyword in self.get_plugin_type(ptype):
                    yield self.get_plugin_type(ptype)[keyword]
        else:
            for keyword in self.get_plugin_type(plugin_type):
                yield self.get_plugin_type(plugin_type)[keyword]

    def _iter_hooks(self, cls, name, *args, **kwargs):
        for plugin in self.iter_plugins():
            for hook in plugin.hooks:
                if not issubclass(hook, cls):
                    continue
                if hook.hookname != name:
                    continue
                yield hook(plugin, *args, **kwargs)

    @contextlib.contextmanager
    def apply_context_hook(self, hookname, *args, **kwargs):
        """Apply a context hook (that is, run stuff before and after a `with` context).

        :param str hookname: Name of the hook to apply.
        :param list args: List of parameters to pass to hooks constructor
        :param dict kwargs: Dictionary of parameters to pass to hooks and
            ``function``.
        """
        with contextlib.ExitStack() as stack:
            for hook in self._iter_hooks(hooks.ContextHook, hookname, *args, **kwargs):
                stack.enter_context(hook)
            yield

    def apply_method_hook(self, hookname, function, *args, **kwargs):
        """Apply a method hook (that is, run stuff before and after a method call).

        :param str hookname: Name of the hook to apply.
        :param function function: Function to which the hook is to be applied.
        :param list args: List of parameters to pass to hooks and
            ``function``.
        :param dict kwargs: Dictionary of parameters to pass to hooks and
            ``function``.
        """
        with contextlib.ExitStack() as stack:
            for hook in self._iter_hooks(hooks.ContextHook, hookname, *args, **kwargs):
                stack.enter_context(hook)
            for hook in self._iter_hooks(hooks.MethodHook, hookname):
                function = hook.wrap(function)
            return function(*args, **kwargs)

    def get_plugin(self, keyword):
        """Return the plugin with the given keyword."""
        for plugin in self.iter_plugins():
            if plugin.keyword == keyword:
                return plugin
        raise NoMatch(keyword, sorted(plugin.keyword for plugin in self.iter_plugins()))

    def get_plugin_type(self, plugin_type):
        """Return a dictionary of plugins of the given type."""
        return self.plugins[plugin_type]

    def iter_pluginkeywords(self, plugin_type=None):
        """Iterate over plugin keywords."""
        for plugin in self.iter_plugins(plugin_type):
            yield plugin.keyword

    def match(self, plugin_type, value):
        """Return the first plugin matching ``value``.

        A plugin ``Foo`` matches ``value`` if ``Foo.match(value)`` returns
        True.
        """
        for plugin in sorted(self.get_plugin_type(plugin_type).values(), reverse=True):
            if plugin.match(value):
                return plugin
        raise NoMatch(value, sorted(self.iter_keywords(plugin_type)))

    def iter_keywords(self, plugin_type=None):
        """Iterate over keywords"""
        if plugin_type is None:
            for ptype in self.plugins:
                yield from self.get_plugin_type(ptype)
        else:
            yield from self.get_plugin_type(plugin_type)
