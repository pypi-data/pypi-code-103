import os
import sys


class PathImporter:
    """The class to import modules from paths."""
    @staticmethod
    def _get_module_name(absolute_path):
        module_name = os.path.basename(absolute_path)
        module_name = module_name.replace('.py', '')
        return module_name

    @staticmethod
    def add_modules(*paths):
        for p in paths:
            if not os.path.exists(p):
                raise FileNotFoundError('cannot import module from %s, file not exist', p)
            module, spec = PathImporter._path_import(p)
        return module

    @staticmethod
    def _path_import(absolute_path):
        import importlib.util
        module_name = PathImporter._get_module_name(absolute_path)
        spec = importlib.util.spec_from_file_location(module_name, absolute_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[spec.name] = module
        return module, spec
