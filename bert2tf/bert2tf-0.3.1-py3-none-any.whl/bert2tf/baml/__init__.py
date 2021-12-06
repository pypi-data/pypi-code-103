import re
from typing import TextIO, Dict, Union, Tuple

import yaml
from yaml.constructor import FullConstructor

from .helper import parse_use_source, Bert2tfLoader, load_py_modules


class BAML:
    @staticmethod
    def register(cls):
        tag = f'!{cls.__name__}'

        try:
            yaml.add_constructor(tag, cls._from_yaml, Loader=Bert2tfLoader)
        except AttributeError:

            def f_y(constructor, node):
                """
                Wrapper function for the constructor.

                :param constructor: yaml constructor
                :param node: to be added
                :return: generator
                """
                return constructor.construct_yaml_object(node, cls)

            yaml.add_constructor(tag, f_y, Loader=Bert2tfLoader)
        return cls

    @staticmethod
    def load(stream: TextIO) -> Union['BAMLCompatible', Dict]:
        r = yaml.load(stream, Loader=Bert2tfLoader)

        return r

    @staticmethod
    def dump(data, stream=None, **kwargs):
        """
        Serialize a Python object into a YAML stream.

        If stream is None, return the produced string instead.

        :param data: the data to serialize
        :param stream: the output stream
        :param kwargs: other kwargs
        :return: the yaml output
        """

        return yaml.dump(
            data, stream=stream, default_flow_style=False, sort_keys=False, **kwargs
        )

    @staticmethod
    def escape(value: str, whitelist: Tuple[str] = None) -> str:
        if whitelist:
            value = re.sub(rf'!({"|".join(whitelist)})', r'use: \1', value)
        else:
            value = re.sub(r'!', r'use: ', value)

        return value

    @staticmethod
    def unescape(value: str, whitelist: Tuple[str] = None, blacklist: Tuple[str] = None) -> str:
        if whitelist:
            r = rf'use: ({"|".join(whitelist)})'
        else:
            r = r'use: (\w+)'

        value = re.sub(r, r'!\1', value)

        if blacklist:
            value = BAML.escape(value, whitelist=blacklist)

        return value


class BAMLCompatibleType(type):
    """
    Metaclass for :class:`BAMLCompatible`.

    It enables any class inherit from :class:`BAMLCompatible` to auto-register itself at :class:`BAML`
    """

    def __new__(cls, *args, **kwargs):
        _cls = super().__new__(cls, *args, **kwargs)
        BAML.register(_cls)
        return _cls


class BAMLCompatible(metaclass=BAMLCompatibleType):
    @classmethod
    def _from_yaml(cls, constructor: FullConstructor, node):
        from .parsers import get_parser

        data = constructor.construct_mapping(node, deep=True)

        return get_parser(cls).parse(cls, data)

    @classmethod
    def load_config(cls, use: str, use_with: Dict = None, metas: Dict = None) -> 'BAMLCompatible':
        """
        Load object from config

        :param use: config source
        :param use_with: class init function parameters
        :param metas: meta parameters for class
        :return: object
        """
        import io
        from ..flow import FlowType
        from ..executors import ExecutorType

        stream = parse_use_source(use)
        with stream:
            # change type like !Flow to use: Flow
            stream = BAML.escape(''.join([line for line in stream.readlines()]))

            config = BAML.load(io.StringIO(stream))

            # update cls init parameters
            if use_with:
                if 'use_with' not in config:
                    config['use_with'] = use_with
                else:
                    config['use_with'].update(use_with)

            # update cls metas parameters
            if metas:
                if 'metas' not in config:
                    config['metas'] = metas
                else:
                    config['metas'].update(metas)

            # if py modules in metas, use class which in py modules to override the class
            # which already existed in bert2tf
            if 'metas' in config and 'py_modules' in config['metas'] and config['metas']['py_modules']:
                load_py_modules(config['metas']['py_modules'])

            stream = BAML.dump(config)

            # change type like use: Flow to !Flow which in white list
            whitelist = ('Flow',) if isinstance(cls, FlowType) else None
            blacklist = (r'\w+Driver',) if isinstance(cls, ExecutorType) else None
            stream = BAML.unescape(stream, whitelist=whitelist, blacklist=blacklist)

            # load obj
            obj = BAML.load(io.StringIO(stream))

        return obj
