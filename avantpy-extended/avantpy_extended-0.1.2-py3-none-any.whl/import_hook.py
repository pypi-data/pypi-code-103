"""A custom importer making use of the import hook capability
"""
import unidecode
import importlib
import yaml
import os
import os.path
import sys

from codeop import CommandCompiler
from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

import friendly_traceback

from . import session
from . import converter
from .my_gettext import gettext_lang
from .wrappers._translated import class_translate, global_translate, fetch_translations, get_index

MAIN_MODULE_NAME = None

friendly_traceback.exclude_file_from_traceback(__file__)

_definitions = {}


def import_main(name):
    """Imports the module that is to be interpreted as the main module.

       avantpy is often invoked with a script meant to be run as the
       main module its source is transformed with the -s (or --source) option,
       as in::

           python -m avantpy -s name

       Python identifies avantpy as the main script, which is not what we want.
    """
    global MAIN_MODULE_NAME
    _ = gettext_lang.lang
    MAIN_MODULE_NAME = name
    try:
        main = importlib.import_module(name)
        return main
    except ModuleNotFoundError:
        print(_("Cannot find main module: "), name)


class AvantPyRenamerLoader(Loader):
    def __init__(self, loader, name, rename):
        self.loader = loader
        self.name = name
        self.rename = rename

    def create_module(self, spec):
        spec.name = self.rename
        spec.loader = self.loader
        mod = self.loader.create_module(spec)
        spec.name = self.name
        spec.loader = self
        #mod = super().create_module(spec)
        return mod

    def exec_module(self, module):
        module.__name__ = self.rename
        mod = self.loader.exec_module(module)
        module.__name__ = self.name
        return mod

    def is_package(self, fullname):
        return self.loader.is_package(fullname.replace(self.name, self.rename))

def _level_down(fullname, dct, package_hierarchy):
    dct['translatedSubmodulesReverse'] = {
        v['mapTo'].split('.')[1]: k
        for k, v in dct['translatedSubmodules'].items()
    }

    if 'mapTo' in dct:
        if len(package_hierarchy) > 2 and package_hierarchy[1] in dct['translatedSubmodules']:
            return _level_down(fullname, dct['translatedSubmodules'][package_hierarchy[1]], package_hierarchy[1:])
        elif len(package_hierarchy) == 2:
            if package_hierarchy[1] in dct['translatedSubmodules']:
                submodule = dct['translatedSubmodules'][package_hierarchy[1]]
                wrapped_name = submodule['mapTo']
                wrapped_package = wrapped_name.split('.')[0] + '@ntr'
                total = [wrapped_package] + wrapped_name.split('.')[1:]
                wrapped_spec = importlib.util.find_spec('.'.join(total), wrapped_package)
                if wrapped_spec:
                    spec = importlib.util.spec_from_loader(
                        fullname,
                        WrappingLoader(wrapped_name, wrapped_spec, submodule)
                    )
                    return spec
            elif package_hierarchy[1] in dct['translatedSubmodulesReverse']:
                wrapped_package = package_hierarchy[0] + '@ntr'
                total = [wrapped_package] + package_hierarchy[1:]
                wrapped_spec = importlib.util.find_spec('.'.join(total), wrapped_package)
                if wrapped_spec:
                    spec = importlib.util.spec_from_loader(
                        '.'.join(package_hierarchy),
                        WrappingLoader('.'.join(package_hierarchy), wrapped_spec, {})
                    )
                    return spec

class AvantPyMetaFinder(MetaPathFinder):
    """A custom finder to locate modules.  The main reason for this code
       is to ensure that our custom loader, which does the code transformations,
       is used."""

    def find_spec(self, fullname, path, target=None):
        """Finds the appropriate properties (spec) of a module, and sets
           its loader."""
        global _definitions

        if not path:
            path = [os.getcwd(), os.path.join(os.path.dirname(__file__), 'wrappers')]
        if "." in fullname:
            name = fullname.split(".")[-1]
        else:
            name = fullname

        top_level = fullname.split('.')[0]

        # avantpy_trans namespace should never have translations of its own
        if top_level == 'avantpy_trans':
            return None
        # we can use the notation @ntr at the end of a package to force
        # the system to use the original, untranslated version
        elif top_level.endswith('@ntr'):
            real_fullname = top_level[:-4] + fullname[len(top_level):]
            real_fullname = importlib.util.resolve_name(real_fullname, None)
            for finder in sys.meta_path[1:]:
                package = top_level[:-4] if '.' in fullname else None
                spec = finder.find_spec(real_fullname, package)
                if spec is not None:
                    break
            else:
                return None
            spec.name = fullname
            total = [top_level[:-4]] + fullname.split('.')[1:]
            rename = '.'.join(total)
            spec.loader = AvantPyRenamerLoader(spec.loader, fullname, rename)
            return spec

        package_hierarchy = fullname.split('.')
        lang = session.state.get_lang()
        # If we have a language, check if this import
        # has recognized translations.
        if lang:
            index = get_index(lang)
            if top_level in index['packages']:
                package_index = index['packages'][top_level]

                if 'name' in package_index:
                    package_name = package_index['name']
                else:
                    package_name = top_level

                if top_level in _definitions:
                    if _definitions[top_level]:
                        dct = _definitions[top_level]
                    else:
                        dct = None
                else:
                    dct = None
                    if 'builtin' not in package_index or not package_index['builtin']:
                        try:
                            dct = importlib.import_module(
                                f'avantpy_trans.{package_name}',
                                'avantpy_trans'
                            ).__dict__[lang]
                        except (ImportError, KeyError):
                            _definitions[top_level] = None
                        else:
                            _definitions[top_level] = dct

                    # If we cannot get the installed package for translations for
                    # this module, try the development and remote YAML versions.
                    if not dct:
                        info = fetch_translations(package_name, lang)
                        if info is not None and os.path.exists(info):
                            with open(info, 'r') as f:
                                dct = yaml.safe_load(f)
                if dct:
                    if 'mapTo' in dct and len(package_hierarchy) == 1:
                        wrapped_name = dct['mapTo']
                        wrapped_package = wrapped_name.split('.')[0] + '@ntr'
                        total = [wrapped_package] + wrapped_name.split('.')[1:]
                        wrapped_spec = importlib.util.find_spec('.'.join(total), wrapped_package)
                        if wrapped_spec:
                            spec = importlib.util.spec_from_loader(
                                fullname,
                                WrappingLoader(wrapped_name, wrapped_spec, dct)
                            )
                            return spec
                    if 'translatedSubmodules' in dct:
                        return _level_down(fullname, dct, package_hierarchy)
                back = suffixes.pop()

        exts = [session.state.get_dialect()]
        if None in exts:
            exts = session.state.all_dialects()

        file_hierarchy = fullname.split('.')
        for ext in exts:
            file_hierarchy[-1] += '.' + ext

            for entry in path:
                filename = os.path.join(entry, *file_hierarchy)
                if os.path.exists(filename):
                    return spec_from_file_location(
                        fullname,
                        filename,
                        loader=AvantPyLoader(filename),
                        submodule_search_locations=None,
                    )
        return None  # Not an AvantPy file


sys.meta_path.insert(0, AvantPyMetaFinder())


class WrappingLoader(Loader):
    def __init__(self, wrapped_name, wrapped_spec, translation_dict = None):
        self.wrapped_spec = wrapped_spec
        self.wrapped_name = wrapped_name
        self.core_map = translation_dict['coreMap'] if translation_dict and 'coreMap' in translation_dict else {}
        self.class_map = translation_dict['classMap'] if translation_dict and 'classMap' in translation_dict else {}
        super().__init__()

    def is_package(self, fullname):
        return self.wrapped_spec.parent == self.wrapped_spec.name

    def create_module(self, spec):
        module = importlib.util.module_from_spec(self.wrapped_spec)
        global_translate(module.__dict__, module, self.core_map)
        return module

    def exec_module(self, module):
        self.wrapped_spec.loader.exec_module(module)
        global_translate(module.__dict__, module, self.core_map)
        class_translate(module, self.class_map)

class AvantPyLoader(Loader):
    """A custom loader which will transform the source prior to its execution"""

    def __init__(self, filename):
        self.filename = filename
        self.compile = CommandCompiler()

    def exec_module(self, module):
        """import the source code, converts it before executing it."""
        if module.__name__ == MAIN_MODULE_NAME:
            module.__name__ = "__main__"

        with open(self.filename, encoding="utf8") as f:
            source = f.read()
        # original = source

        _path, extension = os.path.splitext(self.filename)
        # name = os.path.basename(_path)
        # fullname = name + extension
        dialect = extension[1:]

        friendly_traceback.cache.add(self.filename, source)
        try:
            session.state.set_dialect(dialect)
            source = converter.convert(source, dialect, filename=self.filename)
        except Exception:
            friendly_traceback.explain()
            return

        # ------------------------
        # Previously, we did the following essentially in one step:
        #
        #     exec(source, vars(module))
        #
        # The problem with that approach is that exec() records '<string>'
        # as the filename, for every file thus loaded; in some cases, the
        # prevented the traceback from having access to the source of the file.
        # By doing it in two steps, as we do here by first using compile()
        # and then exec(), we ensure that the correct filename is attached
        # to the code objects.
        # -------------------------

        try:
            code_obj = compile(source, self.filename, "exec")
        except Exception:
            friendly_traceback.explain()

        try:
            exec(code_obj, vars(module))
        except Exception as e:
            friendly_traceback.explain()
        return
