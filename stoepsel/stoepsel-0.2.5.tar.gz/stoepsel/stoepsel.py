# -*- coding: utf-8 -*-
#
# stoepsel.py
#
# Copyright 2021 Jens Rapp (rapp.jens@gmail.com)
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
'''
This is the core of stoepsel plugin system
'''
import importlib.util
import logging
import sys
import os
import re


basicConfig = {
    'plugin_path' : 'plugins',
    'plugin_config' : {}
}


class PluginError(RuntimeError):
    '''
    PluginManager raises this
    '''
    pass

class LoggingClass():
    '''
    this baseclass allows logging for all items
    todo: automatic setup of logging ?
    '''
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)


class EntryPointConnector(LoggingClass):
    '''
    since both, Plugin and PluginManager use the entrypoint space,
    they derive from this super class which gives them the ability
    to handle the entrypoint space
    '''
    PGM_MAIN = '__main__'

    def __init__(self, modeltree = None):
        super().__init__()
        '''
        initialize with a given or new entrypoint space
        '''
        if modeltree is not None:
            self.__model_tree = modeltree
        else:
            self.__model_tree = {
                'config:' : {},
                'plugins:' : {},
            }
        self.logger.debug(f'my model_tree: {self.__model_tree}')

    def get_item(self, path, default=None):
        '''
        get an item out of the model_tree
        path is a slash delimited name path
        '''
        self.logger.debug(f'searching for entrypoint {path}')
        if path == '/':
            return self.__model_tree

        p = path.split('/')
        d = self.__model_tree
        for item in p:
            if item in d:
                d = d[item]
            else:
                return default
        return d

    def __merge(self, this, other):
        '''
        for internal use only.
        it merges two dictionaries
        '''
        self.logger.debug(f'merging with {other}')
        self.logger.debug(f'merging into {this}')

        for k, v in other.items():
            if (k in this and isinstance(this[k], dict)):
                self.__merge(this[k], other[k])
            else:
                this[k] = other[k]

    def __path_to_dict(self, path, value):
        '''
        creates a dictionarized path with a single value
        '''
        p = path.split('/')[::-1]
        d = value
        for pos in p:
            newdict = {}
            newdict[pos] = d
            d = newdict
        return d

    def register(self, path, obj):
        '''
        registers a node in model_tree
        this is utilized to use objects or functions from other plugins
        '''
        self.logger.debug(f'registering {obj} at {path}')
        p = self.__path_to_dict(path, obj)
        self.__merge(self.__model_tree, p)

    @property
    def plugins(self):
        '''
        get plugin path of model_tree
        '''
        return self.get_item('plugins:', {})

    @property
    def config(self):
        '''
        get config path of model tree
        '''
        return self.get_item('config:', {})


class PluginVersion(LoggingClass):
    '''
    the plugin version is able to organize and compare versions numbers
    '''
    # this is the delimiter for a version
    VERSION_DELIMITER = '##'

    def __init__(self, value):
        super().__init__()
        '''
        initialize with `value`.
        this can be a string (like 1.0.1), a tuple (1,1,1) or another
        intance of PluginVersion
        '''
        if isinstance(value, str):
            versionvalue = value.split(PluginVersion.VERSION_DELIMITER)[-1]
            self.version = tuple(map(int, (versionvalue.split("."))))
        elif isinstance(value, PluginVersion):
            self.version = value.version
        elif isinstance(value, tuple):
            self.version = value
        else:
            raise PluginError(f'Value type {type(value)} of {value} unknown')
        self.logger.debug(f'having version {self.version}')

    def match(self, expression):
        '''
        this is where matching magic happens.. some day..
        todo
        '''
        self.logger.debug('matching {expression}')

        check = {
            '>=' : lambda t : self.version >= t.version,
            '>' : lambda t : self.version > t.version,
            '<' : lambda t : self.version < t.version,
            '<=' : lambda t : self.version <= t.version,
            '!=' : lambda t : self.version != t.version,
            '==' : lambda t : self.version == t.version
        }
        match = True

        versionlist = expression.split(';')
        self.logger.debug(versionlist)

        for version in versionlist:
            # find the first number or dot.
            index = re.search('\d', version).start()

            pattern = version[:index]
            if pattern == '':
                pattern = '=='

            fversion = PluginVersion(version[index:])

            self.logger.debug (f'Pattern = "{pattern}"')

            if pattern in check:
                if not check[pattern](fversion):
                    match = False

        return match

    def __eq__(self, version):
        if isinstance(version, PluginVersion):
            return self.version == version.version
        return self.version == version

    def __lt__(self, version):
        if isinstance(version, PluginVersion):
            return self.version < version.version
        return self.version < version

    def __le__(self, version):
        return self == version or self < version

    def __gt__(self, version):
        return not self <= version

    def __ge__(self, version):
        return not self < version

    def __repr__(self):
        return '.'.join(self.version)


class Plugin(EntryPointConnector):
    '''
    This is the Plugin base class.
    Any plugin has to derive from this
    it needs to set the static information
    :name as unique string
    :version as string, has to start with a number.
    dependencies a list of dependencies as string in the form `name##version`
    Currently only a hard version can be set. more flexible version ranges are
    ought ro be done.
    '''

    # name of the plugin
    name = 'base',
    # version of the plugin
    version = '0.0.1',
    # dependencies of the plugin
    dependencies = []

    def match_version(self, specifier):
        '''
        static function
        matches the version range for this module
        WARNING! currently only matches ! <
        '''
        self.logger.debug(f'matching versions')
        return PluginVersion(self.version).match(specifier)

    def __init__(self, config = {}, model_tree = {}):
        super().__init__(model_tree)
        '''
        initialize the plugin giving a plugin config
        don't use this method in your plugins. There is a setup() method
        you can utilize to initialize your plugin. self.config and
        self.__model_tree will already be there then.
        '''
        self.logger.info('plugin initialization started')
        #self.setup()


    def _get_arg(self, arg, **kwargs):
        '''
        get an argument from **kwargs- just a helper function you might want
        to use
        '''
        if arg in kwargs.keys:
            return kwargs[arg]
        return None

    def setup(self):
        '''
        use this to initialize your plugin
        '''
        pass


class PluginManager(EntryPointConnector):
    '''
    PluginManager attempts to load plugins from plugin path and runs them
    It resolves dependencies recursively and has simple version matching.

    '''
    PLUGIN_EXCLUDES = ['__pycache__', 'README', 'README.md', 'deactivated']

    def __init__(self, config=basicConfig):
        '''
        initialize with a given config
        '''
        super().__init__()

        self.config.update(config)

        sys.path.append(self.config['plugin_path'])

        modules = self.discover_plugins()
        self.logger.info(f'discovered {modules}, resolving..')
        self.resolve_plugins(modules)
        self.logger.info(f'starting plugins {self.plugins}')
        self.start_plugins()

    def instanciate_module(self, module_name, module):
        '''
        create a module instance if possible
        '''
        #get module config if possible
        self.logger.debug(f'attempting to instanciate {module.name}')
        mod_cfg = {}
        if module_name in self.config['plugin_config']:
            mod_cfg = self.config['plugin_config'][module_name]
            self.logger.info(f'{module_name} has config')
            self.logger.debug(f'{mod_cfg}')

        instance = module(mod_cfg, self.get_item('/'))
        self.logger.debug(f'module instance {instance}')
        return instance

    def module_from_file(self, module_name, file_path):
        '''
        read a file
        '''
        module = None
        if os.path.isfile(file_path):
            self.logger.debug(
                    f'attempting to read {module_name} from {file_path}'
                    )
            spec = importlib.util.spec_from_file_location(
                    module_name, file_path
                    )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            # TODO: load packages
            pass
        return module

    def get_plugins_from_module(self, module):
        '''
        find all classes in module
        '''
        retval = {}
        for n, c in module.__dict__.items():
            self.logger.debug(f'checking element {n} for plugin capabilities')
            if isinstance(c, type) \
                and issubclass(c, Plugin) \
                and not n == 'export'  \
                and not n == 'Plugin':
                    self.logger.debug(f'{n} is a plugin')
                    retval[n] = c

        return retval

    def discover_plugins(self):
        '''
        look for plugins in plugin_path
        '''
        cfg_path = self.config['plugin_path']
        modules = {}
        self.logger.debug(f'searching files in {cfg_path}')
        for file in os.listdir(cfg_path):
            filename = os.path.join(cfg_path, file)
            if os.path.isfile(filename):
                # get module and module path
                # import module
                module_file = os.path.split(filename)[-1]
                module_name = os.path.splitext(module_file)[0]
                logging.info(f'reading file  {filename}')

                mod = self.module_from_file(module_name, filename)

                # create instance
                # instance = self.instanciate_module(module_name, mod)
                # find plugins in module
                for cname, cls in self.get_plugins_from_module(mod).items():
                    instance = self.instanciate_module(cname, cls)
                    modules[instance.name] = instance

        return modules

    def check_plugin_dependencies(self, modules, module, version=None, dejavu=[]):
        '''
        checks if dependencies of a module can be resolved and sorts
        plugins by dependency
        Additionally, it checks cyclic dependencies
        '''
        self.logger.debug(f'checking dependencies for {module}')
        # dependency brake
        if module in dejavu:
            self.logger.error(f'Cyclic dependency in {module}')
            raise PluginError(f'Cyclic dependency error in {module}')

        if module in self.plugins:
            # dependency has already been fullfilled
            self.logger.debug(f'Dependency {module} already fullfilled')
            return True

        if not module in modules:
            self.logger.error(f'Plugin {module} does not exist!')
            raise PluginError(f'Module {module} not in modules list')

        mod = modules[module]
        # check module version
        if version is not None:
            self.logger.debug(f'Checking version for {module}')
            if not mod.match_version(version):
                self.logger.error(f'Plugin version {mod} does not match {version}')
                return False

        if len(mod.dependencies) == 0:
            self.logger.debug(f'Plugin {module} has no dependencies')
            return True

        # check dependencies
        resolved = False
        for dependency in mod.dependencies:
            # for each dependency
            # check resolve dependency
            name, version = dependency.split(PluginVersion.VERSION_DELIMITER)

            # append list for cyclic dependency check
            ndejavu = list(dejavu)
            ndejavu.append(module)

            self.logger.info(f'Module {module} depends on {dependency}')
            resolved = self.check_plugin_dependencies(
                    modules,
                    name,
                    version,
                    ndejavu
                    )

        # append this module to dependency list
        if resolved:
            self.logger.info(f'Dependencies for {module} resolved. appending..')
            self.plugins[module] = modules[module]
        else:
            self.logger.error(f'Could not resolve dependencies for {module}')
            return False
        return resolved

    def resolve_plugins(self, modules):
        '''
        sorts plugins and looks if dependencies can be resolved.
        dependencies are directly
        '''
        for module in modules:
            if not self.check_plugin_dependencies(modules, module):
                raise PluginError(f'Dependency check for {module} failed.')

    def start_plugins(self):
        '''
        run setup for all plugins
        '''
        for module_name in self.plugins.keys():
            self.plugins[module_name].setup()
