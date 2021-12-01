#
# SPDX-License-Identifier: MIT
#
# Copyright (C) 2019-2021, AllWorldIT.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""EZPlugins manager."""

import importlib
import inspect
import logging
import pkgutil
from types import ModuleType
from typing import Dict, Iterator, List, Optional, Tuple

from .exceptions import EZPluginMethodNotFoundException
from .plugin import EZPlugin, EZPluginMethod


class EZPluginModule:
    """
    Representation of a module within the plugin package hierarchy, which may contain plugins.

    If there is no plugins and no load exception, the module will not be added to the modules list.

    See :attr:`ezplugins.manager.EZPluginManager.modules` for how to get a list of loaded modules.

    Parameters
    ----------
    module_name : str
        Name of the module.

    """

    _module: Optional[ModuleType]
    _module_name: str
    _plugins: List[EZPlugin]
    _load_exception: Optional[Exception]

    def __init__(self, module_name: str):
        """
        Representation of a module within the plugin package hierarchy, which may contain plugins.

        If there is no plugins and no load exception, the module will not be added to the modules list.

        See :attr:`ezplugins.manager.EZPluginManager.modules` for how to get a list of loaded modules.

        Parameters
        ----------
        module_name : str
            Name of the module.

        """

        # Start off with the module being None and an empty plugin list
        self._module = None
        self._module_name = module_name
        self._plugins = []

        # Try import
        try:
            self._module = importlib.import_module(module_name)
        except Exception as exception:  # pylint: disable=broad-except
            # If we failed, set the status and return
            self._load_exception = exception
            return

        # Loop with class names
        for (_, plugin_class) in inspect.getmembers(self._module, inspect.isclass):

            # Only add classes that were marked as EZPlugins
            if not getattr(plugin_class, "_is_ezplugin", False):
                continue
            # Save plugin
            self._plugins.append(EZPlugin(plugin_class()))
            logging.debug("EZPlugin loaded from '%s', class '%s'", self.module_name, plugin_class)

        self._load_exception = None

    @property
    def module(self) -> Optional[ModuleType]:
        """
        Property containing the imported module.

        Returns
        -------
        Optional[ModuleType]
            Module that was imported (if it was imported, or None).

        """
        return self._module

    @property
    def module_name(self) -> str:
        """
        Property containing the name of the module.

        Returns
        -------
        str
            Module name.

        """
        return self._module_name

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Property containing a list of EZPlugin's that belong to this module.

        Returns
        -------
        List[EZPlugin]
            List of instantiated EZPlugin's that represent the plugin objects that were instantiated.

        """
        return self._plugins

    @property
    def load_exception(self) -> Optional[Exception]:
        """
        Property containing an exception if one was raised during load.

        Returns
        -------
        Optional[Exception]
            An exception raised during load if any, or None otherwise.

        """
        return self._load_exception


class EZPluginManager:
    """
    The EZPluginManager is responsible for both loading and returning plugin methods for execution.

    Plugins are loaded by specifying the plugin package names. These packages are recursed and all classes decorated as being
    EZPlugins are instantiated::

        import ezplugins

        # Load plugins from mypackage.plugins and "mypackage2.plugins"
        plugin_manager = ezplugins.EZPluginManager(["mypackage.plugins", "mypackage2.plugins"])

    Plugins are loaded from packages which are looked up within ``PYTHONPATH``.

    Packages are recursed and all plugins are loaded by instantiating the classes marked as plugins. The resulting instantiated
    objects are used when methods are run.

    Plugins are mapped using their fully qualified name ``full.module.name#ClassName`` and their class name ``#ClassName``. Aliases
    can be created used for grouping or easier reference using :func:`ezplugins.decorators.ezplugin_metadata`.

    For calling plugin methods see :meth:`ezplugins.manager.EZPluginManager.methods`.

    Parameters
    ----------
    plugin_packages : List[str]
        Source packages to load plugins from.

    """

    _modules: List[EZPluginModule]

    def __init__(self, plugin_packages: List[str]):
        """
        Initialize EZPluginsCollection using a list of plugin base packages.

        Plugins are mapped with the below names:
            full.module.name#ClassName
            #ClassName

        Calling a plugin by name where multiple names match will result in all plugins being called.

        Parameters
        ----------
        plugin_packages : List[str]
            Source packages to load plugins from.

        """

        # Initialize the module list we loaded plugins from
        self._modules = []

        # Load plugins
        self._load_plugins(plugin_packages)

    def methods(
        self,
        where_name: Optional[str] = None,
        from_plugin: Optional[str] = None,
    ) -> Iterator[Tuple[EZPluginMethod, EZPlugin]]:
        """
        Return a generator used to iterate over plugin methods with a specific name and optionally from a specific plugin.

        An example of running all ``some_func`` methods in all plugins can be found below::

            # Call the method some_func in each plugin
            for method, _ in plugin_manager.methods(with_name="some_func"):
                result = method.run("param1", "param2")
                print(f"RESULT: {result}")

        As you can see in the above examples we have a ``_`` in the `for`, this is the :class:`ezplugins.plugin.EZPlugin` plugin
        object which we didn't need::

            # Call the method some_func in each plugin
            for method, plugin in plugin_manager.methods(with_name="some_func"):
                result = method.run("param1", "param2")
                print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")

        One can also call every single method marked as an EZPlugin method in all plugins using the following::

            # Call the method some_func in each plugin
            for method, _ in plugin_manager.methods():
                result = method.run("param1", "param2")
                print(f"RESULT: {result}")

        Calling a plugin by name where multiple names match based on class or alias will result in all plugins being called.

        Parameters
        ----------
        where_name : Optional[str]
            Limit methods returned to those matching the name provided.

        from_plugin : Optional[str]
            Limit methods returned to those belonging to a specific plugin.

        Returns
        -------
        Iterator[Tuple[EZPluginMethod, EZPlugin]]
            A generator that provides tuples in the format of (EZPluginMethod, EZPlugin).

        """

        # Work out the plugins and methods we're going to call
        # Methods are unique, we'll be calling in order of method.order
        found_methods: Dict[EZPluginMethod, EZPlugin] = {}

        # Loop with our plugins matching the provided plugin_name or None
        for plugin in [x for x in self.plugins if from_plugin in [None, x.fqn, x.name, x.alias]]:
            # Loop with methods matching the method name
            for method in [x for x in plugin.methods if where_name in [None, x.name]]:
                # Check if plugin is in our call queue
                found_methods[method] = plugin

        # If we didn't find any methods, raise an exception
        if not found_methods:
            raise EZPluginMethodNotFoundException(method_name=where_name, plugin_name=from_plugin)

        # Loop with the ordered methods
        for method, plugin in sorted(found_methods.items(), key=lambda x: x[0].order):
            print(f"ITERATOR METHOD: {plugin.fqn} => {method.name} [execution order: {method.order}]")
            yield (method, plugin)

    def get_plugin(self, plugin_name: str) -> set[EZPlugin]:
        """
        Return a plugin with a given name.

        This will match on the fully qualified plugin name, the class name and aliase.

        Parameters
        ----------
        plugin_name : str
            Plugin to call the method in.

        Returns
        -------
        set[EZPlugin]
            Set of EZPlugin objects which matches the criteria.

        """

        plugin_set = set()

        # Loop with our plugins
        for plugin in self.plugins:
            # Add plugins which match the specified name
            if plugin_name in (plugin.fqn, plugin.name, plugin.alias):
                plugin_set.add(plugin)

        return plugin_set

    #
    # Internals
    #

    def _load_plugins(self, plugin_packages: List[str]) -> None:
        """
        Load plugins from the plugin_package we were provided.

        Parameters
        ----------
        plugin_packages : List[str]
            List of plugin package names to load plugins from.

        """

        # Find plugins in the plugin packages
        for plugin_package in set(plugin_packages):
            self._find_plugins(plugin_package)

    def _find_plugins(self, package_name: str) -> None:  # noqa: C901, pylint: disable=too-many-branches
        """
        Recursively search the package package_name and retrieve all plugins.

        Classes ending in "Base" are excluded.

        Parameters
        ----------
        package_name : str
            Package to load plugins from.

        """

        logging.debug("Finding plugins in '%s'", package_name)

        package = EZPluginModule(package_name)

        # Add base package module, but only if it has plugins
        if package.plugins or package.load_exception:
            self._modules.append(package)

        if not package.module:
            return

        # Grab some things we'll need below
        base_package_path = package.module.__path__  # type: ignore
        base_package_name = package.module.__name__

        # Iterate through the modules
        for _, module_name, ispkg in pkgutil.iter_modules(base_package_path, base_package_name + "."):
            # If this is a sub-package, we need to process it later
            if ispkg:
                self._find_plugins(module_name)
                continue
            # Grab plugin module
            plugin_module = EZPluginModule(module_name)
            # If we loaded OK and don't have plugins, don't add to the plugin modules list
            if not plugin_module.plugins and not plugin_module.load_exception:
                logging.debug("Ignoring plugin module '%s': No plugins", plugin_module.module_name)
                continue
            # Add to the plugin modules list
            logging.debug("Adding plugin module: %s (%s plugins)", plugin_module.module_name, len(plugin_module.plugins))
            self._modules.append(plugin_module)

    #
    # Properties
    #

    @property
    def modules(self) -> List[EZPluginModule]:
        """
        List of :class:`ezplugins.manager.EZPluginModule` modules loaded.

        The purpose of this method would potentially be to see if a module failed load using something like the below::

            for module in plugin_manager.modules:
                if module.load_exception:
                    print(f"Module {module.name} failed load: {module.load_exception}")

        Returns
        -------
        List[EZPluginModule]
            Modules loaded during the course of finding plugins.

        """

        return self._modules

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Return a list of plugins loaded in all modules.

        Returns
        -------
        List[EZPlugin]
            List of all plugins loaded.

        """

        plugins = []
        for module in self.modules:
            # Add plugins to our list
            plugins.extend(module.plugins)

        return plugins
