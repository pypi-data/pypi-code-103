import os
from collections.abc import Hashable
from typing import TextIO, Tuple, Optional, List, Union

from yaml import MappingNode
from yaml.composer import Composer
from yaml.constructor import FullConstructor, ConstructorError
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from ..helper import complete_path
from ..importer import PathImporter

__all__ = ['Bert2tfLoader', 'parse_use_source', 'load_py_modules']


class Bert2tfConstructor(FullConstructor):
    """Convert List into tuple when doing hashing."""

    def get_hashable_key(self, key):
        """
        Get the hash value of key.

        :param key: key value to be hashed.
        :return: Hash value of key.
        """
        try:
            hash(key)
        except:
            if isinstance(key, list):
                for i in range(len(key)):
                    if not isinstance(key[i], Hashable):
                        key[i] = self.get_hashable_key(key[i])
                key = tuple(key)
                return key
            raise ValueError(f'unhashable key: {key}')
        return key

    def construct_mapping(self, node, deep=True):
        """
        Build the mapping from node.

        :param node: the node to traverse
        :param deep: required param from YAML constructor
        :return: Mapped data
        """
        if isinstance(node, MappingNode):
            self.flatten_mapping(node)
        return self._construct_mapping(node, deep=deep)

    def _construct_mapping(self, node, deep=True):
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None,
                None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark,
            )
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=True)
            if not isinstance(key, Hashable):
                try:
                    key = self.get_hashable_key(key)
                except Exception as exc:
                    raise ConstructorError(
                        'while constructing a mapping',
                        node.start_mark,
                        'found unacceptable key (%s)' % exc,
                        key_node.start_mark,
                    )
            value = self.construct_object(value_node, deep=deep)

            mapping[key] = value
        return mapping


class Bert2tfLoader(Reader, Scanner, Parser, Composer, Bert2tfConstructor, Resolver):
    """
    The bert2tf loader which should be able to load YAML safely.

    :param stream: the stream to load.
    """

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Bert2tfConstructor.__init__(self)
        Resolver.__init__(self)


def parse_use_source(source: str) -> TextIO:
    """
    Parse config source with converting all sources to TextIO

    :param source: config source
    :return: text io
    """
    import io
    import re
    from pkg_resources import resource_filename
    from ..helper import complete_path

    if source.startswith('_'):
        source = resource_filename('bert2tf', '/'.join(('resources', f'executors.{source}.yml')))

    elif re.fullmatch(r'\w+( \{\})?', source):
        # for adapt driver
        if '{}' in source:
            source = source.replace('{}', '').strip()
        return io.StringIO('!%s\nuse_with: {}' % source)

    elif not os.path.exists(source):
        source = complete_path(source)

    return open(source, 'r', encoding='utf-8')


def load_py_modules(mod: Union[List[str], str], extra_search_paths: Optional[Tuple[str]] = None) -> None:
    """
    Find 'py_modules' in the dict recursively and then load them.

    :param mod: the py modules file path
    :param extra_search_paths: any extra paths to search
    """

    if isinstance(mod, str):
        mod = [mod]

    mod = [complete_path(m, extra_search_paths) for m in mod]
    PathImporter.add_modules(*mod)
