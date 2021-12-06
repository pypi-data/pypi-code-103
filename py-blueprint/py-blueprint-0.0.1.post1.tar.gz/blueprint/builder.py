# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import importlib
import inspect
from typing import Optional, List, Any
import yaml

from .context import Context


def _last_index(lst, element):
    """Get the last index of the element in a list.
    """
    return len(lst) - 1 - lst[::-1].index(element)


def instantiate_object(name: str, package: Optional[str] = None):
    """Instantiate an object defined in a Python source.

    Example:

        >>> instantiate_object('a.ClassA') # a ClassA type object from module a
        # a ClassB type object from module a.b
        >>> instantiate_object('..b.ClassB', package='a.c')

    Args:
        name (str): The name of the object. Support prefixing with additional package
            paths like `package_name.ObjectName`.
        package (str): The name of the package where the object is defined.

    Returns:
        Any: The instantiated object.

    """
    if '.' in name:
        # import module object first
        dot_index = _last_index(name, '.')
        module_name = name[:dot_index]
        class_name = name[dot_index+1:]
        module_object = importlib.import_module(module_name, package)
    else:
        if package is None:
            raise RuntimeError(
                f'A package name must be given to instantiate "{name}". '
                f'Otherwise, you should use a full class name that '
                f'contains its package path.')
        # `name` is a class name
        module_object = importlib.import_module(package)
        class_name = name
    if hasattr(module_object, class_name):
        return getattr(module_object, class_name)
    if hasattr(module_object, '__init__'):
        init = getattr(module_object, '__init__')
        if hasattr(init, class_name):
            return getattr(init, class_name)
    raise RuntimeError(
        f'Failed to find the class {class_name} in either '
        f'{module_object} or its __init__ file.')


def get_package_attributes(package: Optional[str]):
    """Get all attributes of a package.
    """
    if package is None:
        return dict()
    module_object = importlib.import_module(package)
    return module_object.__dict__


def _get_cfg_id(cfg_file: str, num_levels_kept: int) -> str:
    suffix = '.yaml'
    assert cfg_file.endswith(suffix)
    path_components = os.path.abspath(
        cfg_file[:-len(suffix)]).replace('\\', '/').split('/')
    path_components = path_components[-num_levels_kept:]
    cfg_id = '.'.join(path_components)
    return cfg_id


class Builder:
    """The builder that builds python objects from YAML files.

    The Builder extends an ordinary YAML parser with following extra functionality:

    1. A YAML dict with an entry `class: SomeClassName` will be parsed as a python object of
        class `SomeClassName`, all other entries will serve as the input arguments to 
        the `__init__` constructor of the class.

    2. A YAML dict with an entry `function: some_function_name` will be parsed as the result
        of the function `some_function_name`, with all other entries serving as the input arguments
        to that function.

    3. A string starting with `$` will be executed as a python script and returns the resulting python object. 
        Some variables or functions are pre-defined when executing these scripts:
          - `PARSE(relative_path_to_another_yaml_file, **kwargs)`: 
          a function that parses another YAML file with the same Builder and returns the parsed object. 
          For example, `$PARSE('../a.yaml', some_arg=some_value)`.
          - `ARGS`: a dict object that contains all the arguments that are fed into `PARSE`.
          - `FILE`: a string storing the path of this YAML file.
          - `RELATIVE(path)`: a function that returns a relative path to `FILE`.
          - `BLOB(path)`: a function that returns a path under the `blob_root` defined by context.
          - `CTX`: the `Context` object.

    4. Remember to include an entry of `package: package_name`, and import the releated classes and functions 
        in `package_name.__init__`, so that the builder can access their definitions for cases 1.-3.

    """
    def __init__(self, context: Context, verbose: bool = True, ignore_custom_parse: bool = False):
        self._ctx = context
        self.verbose = verbose
        self.ignore_custom_parse = ignore_custom_parse
        self._cfg_file_paths = [None]
        self._packages = [None]
        self._args_stack = [None]

    def _print(self, msg):
        if self.verbose:
            print(f'blueprint: {msg}')

    def parse_cfg_file(self, cfg_file_path, **kwargs):
        args = kwargs

        # xxx/xxx/xxx.yaml:a/b/c
        if ':' in cfg_file_path:
            cfg_file_path, inner_tree_path = cfg_file_path.split(':')
            inner_tree_path = inner_tree_path.split('/')
        else:
            inner_tree_path = []

        if self._cfg_file_paths[-1] is not None:
            cfg_file_path = os.path.join(
                os.path.dirname(self._cfg_file_paths[-1]), cfg_file_path)
        self._cfg_file_paths.append(cfg_file_path)
        self._args_stack.append(args)

        tree_data = yaml.safe_load(open(cfg_file_path, 'r'))
        self._print(f'Parsing {cfg_file_path}')

        if isinstance(tree_data, dict):
            package = tree_data.get('package', None)
        else:
            package = None
        for part in inner_tree_path:
            package = tree_data.get('package', package)
            tree_data = tree_data[part]
        if package is not None:
            self._packages.append(package)

        result = self.parse_cfg_object(tree_data)

        if package is not None:
            self._packages.pop()
        self._cfg_file_paths.pop()
        self._args_stack.pop()
        return result

    def blob_path(self, p):
        return os.path.join(self._ctx.blob_root, p)

    def states_path(self, cfg_file: str, num_levels_kept: int = 2):
        p = os.path.join(self._ctx.blob_root, 'states',
                         self._ctx.exp_name, _get_cfg_id(cfg_file, num_levels_kept))
        assert p.startswith(self._ctx.blob_root)
        return p

    def outputs_path(self, cfg_file: str, num_levels_kept: int = 2):
        p = os.path.join(self._ctx.blob_root, 'outputs',
                         self._ctx.exp_name, _get_cfg_id(cfg_file, num_levels_kept))
        assert p.startswith(self._ctx.blob_root)
        return p

    def relative_path(self, p: str):
        if self._cfg_file_paths[-1] is None:
            raise RuntimeError(
                f'No configuration file found, failed to compute the relative path of {p}.')
        return os.path.relpath(p, os.path.dirname(self._cfg_file_paths[-1]))

    def parse_cfg_object(self, cfg):
        ret = cfg

        if isinstance(cfg, str):
            if cfg.startswith('$$'):
                cfg = cfg.strip()
                arg_name = cfg[len('$$'):]
                ret = self._args_stack[-1][arg_name]

            elif cfg.startswith('$'):
                import math
                import numpy as np
                import torch

                try:
                    ret = eval(cfg[1:], dict(), {
                        'PARSE': self.parse_cfg_file,
                        'ARGS': self._args_stack[-1],
                        'FILE': self._cfg_file_paths[-1],
                        'RELATIVE': self.relative_path,
                        'BLOB': self.blob_path,
                        'STATES': self.states_path,
                        'OUTPUTS': self.outputs_path,
                        'CTX': self._ctx,
                        'os': os,
                        'math': math,
                        'np': np,
                        'torch': torch,
                        **get_package_attributes(self._packages[-1])
                    })
                except Exception as e:
                    self._print(f'Error when evaluating {cfg[1:]}')
                    self._print(f'Current package stack: {self._packages}')
                    raise

        elif isinstance(cfg, dict):
            if 'package' in cfg:
                package = cfg['package']
                del cfg['package']
                self._packages.append(package)
                ret = self.parse_cfg_object(cfg)
                self._packages.pop()
            else:
                if 'class' in cfg or 'function' in cfg:
                    instant_t = None
                    is_class = None
                    if 'class' in cfg:
                        instant_t = instantiate_object(
                            cfg['class'], self._packages[-1])
                        is_class = True
                    if 'function' in cfg:
                        if instant_t is not None:
                            raise RuntimeError(
                                'definition conflict: "class" and "function" '
                                'cannot appear under the same level')
                        instant_t = instantiate_object(
                            cfg['function'], self._packages[-1])
                        is_class = False

                    instant_t.__builder__ = self

                    input_args_dict = {key: val for key, val in cfg.items() if
                                       key not in {'class', 'function'}}

                    # update input_args_dict if the class/function has a '__parse_inputs__' member function
                    if hasattr(instant_t, '__parse_inputs__') and not self.ignore_custom_parse:
                        parse_inputs_fn = getattr(
                            instant_t, '__parse_inputs__')
                        input_args_to_parse = []
                        parse_inputs_fn_argnames = inspect.getfullargspec(
                            parse_inputs_fn).args
                        for arg_name in parse_inputs_fn_argnames:
                            input_args_to_parse.append(
                                input_args_dict[arg_name])
                        parsed_input_args = parse_inputs_fn(
                            *input_args_to_parse)
                        if not isinstance(parsed_input_args, tuple):
                            parsed_input_args = (parsed_input_args,)
                        if len(parsed_input_args) != len(parse_inputs_fn_argnames):
                            raise RuntimeError(
                                f'The __parse_inputs__ function should have the same number of inputs '
                                f'({len(parse_inputs_fn_argnames)}) and outputs ({len(parsed_input_args)})')
                    else:
                        parse_inputs_fn_argnames = []
                        parsed_input_args = []

                    for arg_name, parsed_arg in zip(parse_inputs_fn_argnames, parsed_input_args):
                        input_args_dict[arg_name] = parsed_arg
                    for arg_name, val in input_args_dict.items():
                        if arg_name not in parse_inputs_fn_argnames:
                            input_args_dict[arg_name] = self.parse_cfg_object(
                                val)

                    # check whether the required args of instant_t contains '_args'
                    if is_class:
                        # detect the args of __init__
                        instant_t_init_args = inspect.getfullargspec(
                            instant_t.__init__).args[1:]  # slice with [1:] to skip the `self` arg
                    else:
                        instant_t_init_args = inspect.getfullargspec(
                            instant_t).args

                    if '_ctx' in input_args_dict:
                        raise RuntimeError(
                            f'The argument "_ctx" is reserved and should not be assigned in `cfg`')

                    # if so, set the lastest args as '_args'
                    if '_ctx' in instant_t_init_args:
                        input_args_dict['_ctx'] = self._ctx

                    ret = instant_t(**input_args_dict)
                else:
                    ret = {name: self.parse_cfg_object(
                        val) for name, val in cfg.items()}

        elif isinstance(cfg, list):
            ret = [self.parse_cfg_object(val) for val in cfg]

        elif isinstance(cfg, tuple):
            ret = tuple([self.parse_cfg_object(val) for val in cfg])

        return ret


def build(context: Context, cfg_file_path: str, **kwargs):
    builder = Builder(context)
    return builder.parse_cfg_file(cfg_file_path, **kwargs)
