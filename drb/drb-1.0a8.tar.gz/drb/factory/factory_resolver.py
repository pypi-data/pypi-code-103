import importlib
import os
import re
import sys
import inspect
import logging
import abc
import uuid
from enum import Enum, auto
from types import ModuleType
from urllib.parse import urlparse
from typing import Callable, Dict, List, Optional, Tuple, Type, Union
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
from importlib.metadata import EntryPoint

from .factory import DrbFactory
from ..node import DrbNode
from ..path import ParsedPath
from ..exceptions import DrbException, DrbFactoryException
from ..utils.url_node import UrlNode


logger = logging.getLogger('DrbResolver')


def is_remote_url(parsed_path):
    """
    Checks if the given parsed URL is a remote URL
    """
    return parsed_path.scheme != '' and parsed_path.scheme != 'file'


class DrbSignatureType(Enum):
    SECURITY = auto(),
    PROTOCOL = auto(),
    CONTAINER = auto(),
    FORMATTING = auto()


class DrbSignature(abc.ABC):
    @property
    @abc.abstractmethod
    def uuid(self) -> uuid.UUID:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def label(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def category(self) -> DrbSignatureType:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def factory(self) -> DrbFactory:
        raise NotImplementedError

    @abc.abstractmethod
    def match(self, node: DrbNode) -> bool:
        raise NotImplementedError


class DrbFactoryResolver(DrbFactory):
    """ The factory resolver

    The factory resolver aims to parametrize the selection of the factory
    able to resolves the nodes according to its physical input.
    """

    __instance = None

    @classmethod
    def __check_signature(cls, signature: DrbSignature):
        """
        Checks if the given signature is valid
        """
        if not isinstance(signature.uuid, uuid.UUID):
            raise DrbFactoryException('uuid property of  DrbSignature must be '
                                      'an UUID')
        if not isinstance(signature.factory, DrbFactory):
            raise DrbFactoryException('factory property of DrbSignature must'
                                      'be a DrbFactory')

    @classmethod
    def __inspect_class_filter(cls, module: ModuleType) -> Callable:
        """
        Generates a filter which allows to retrieve classes defined in the
        given module (without classes imported in this module)
        """
        return lambda m: inspect.isclass(m) and m.__module__ == module.__name__

    @classmethod
    def __load_signature(cls, entry: EntryPoint) -> DrbSignature:
        """
        Retrieves the signature node defined in the given entry point.
        :param entry: plugin entry point
        :type entry: EntryPoint plugin entry point
        :returns: the specific implemented factory
        :rtype: DrbSignature
        :raises:
            * DrbFactoryException If no DrbSignature is found.
        """
        try:
            module = importlib.import_module(entry.value)
        except ModuleNotFoundError:
            raise DrbFactoryException(f'Module not found: {entry.value}')

        is_class = cls.__inspect_class_filter(module)
        for name, obj in inspect.getmembers(module, is_class):
            if obj != DrbSignature and issubclass(obj, DrbSignature):
                signature = obj()
                cls.__check_signature(signature)
                return signature
        raise DrbFactoryException(
            f'No DrbSignature found in module: {entry.value}')

    @classmethod
    def __load_drb_signatures(cls, drb_metadata: str) -> \
            Dict[uuid.UUID, DrbSignature]:
        """
        Loads all DRB plugin defined in the current environment
        :returns: A dict mapping factory names as key to the corresponding
            factory
        :rtype: dict
        """
        impls = {}
        plugins = entry_points(group=drb_metadata)

        if not plugins:
            logger.warning('No DRB plugin found')
            return impls

        for name in plugins.names:
            if name not in impls.keys():
                try:
                    signature = DrbFactoryResolver.__load_signature(
                        plugins[name])
                    impls[signature.uuid] = signature
                except DrbFactoryResolver:
                    message = f'Invalid DRB plugin: {name}'
                    logger.warning(message)
                    raise DrbFactoryException(message)
            else:
                logger.warning(f'DRB plugin already loaded: {name}')

        return impls

    def __init__(self):
        self.__signatures = self.__load_drb_signatures('drb.impl')
        self.__protocols = [s for k, s in self.__signatures.items()
                            if s.category == DrbSignatureType.PROTOCOL]
        self.__main_containers = self.__retrieve_main_containers(DrbSignature)
        self.__formats = [s for k, s in self.__signatures.items()
                          if s.category == DrbSignatureType.FORMATTING]

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DrbFactoryResolver, cls).__new__(cls)
        return cls.__instance

    def _create(self, node: DrbNode) -> DrbNode:
        signature, base_node = self.resolve(node)
        if base_node is None:
            return signature.factory.create(node)
        return signature.factory.create(base_node)

    def __retrieve_main_containers(self, cls: Type) -> List[DrbSignature]:
        """
        Retrieves the list of all container signature not having as parent
        class another than the given class.

        :returns: a list of container signature
        :rtype: list
        """
        containers = []
        for k, s in self.__signatures.items():
            if s.category == DrbSignatureType.CONTAINER and \
                    s.__class__ in cls.__subclasses__():
                containers.append(s)
        return containers

    def __retrieve_protocol(self, node: DrbNode) -> Optional[DrbSignature]:
        """
        Retrieves the protocol signature associated to the given node.

        :param node: node which need to be resolved
        :type node: DrbNode
        :returns: a protocol signature or None if no protocol signature match
            the given node
        :rtype: DrbSignature
        """
        for protocol in self.__protocols:
            if protocol.match(node):
                return protocol
        return None

    def __retrieve_container(self, node: DrbNode) -> Optional[DrbSignature]:
        """
        Retrieves the container signature associated to the given node.
        :param node: node which need to be resolved
        :type node: DrbNode
        :returns: a signature matching the given node, otherwise None
        :rtype: DrbSignature
        """
        for s in self.__main_containers:
            if s.match(node):
                return self.__finest_container(node, s)
        return None

    def __finest_container(self, node: DrbNode, finest: DrbSignature) \
            -> DrbSignature:
        """
        Retrieves the finest container signature associated to the given node.
        :param node: node which need to be resolved
        :type node: DrbNode
        :param finest: the current finest signature matching with the given
            node
        :type finest: DrbSignature
        :returns: a signature matching the given node
        :rtype: DrbSignature
        """
        signatures = self.__retrieve_main_containers(finest.__class__)
        for s in signatures:
            if s.match(node):
                return self.__finest_container(node, s)
        return finest

    def __retrieve_formatting(self, node) -> Optional[DrbSignature]:
        """
        Retrieves the formatting signature associated to the given node.

        :param node: node which need to be resolved
        :type node: DrbNode
        :returns: a signature matching the given node, otherwise None
        :rtype: DrbSignature
        """
        for s in self.__formats:
            if s.match(node):
                return s
        return None

    def __create_from_url(self, url: str, curl: str = None,
                          path: List[str] = None) -> DrbNode:
        """
        Parses the given url to retrieve the targeted resource to open as node
        This method allows to target an inner resource (e.g. a XML file in a
        zipped data from a HTTP URL)

        @param url: targeted resource URL
        @type url: str
        @param curl current URL (internal processing)
        @type curl: str
        @param path remaining path of the given URL (internal processing)
        @type path: list
        @return a DrbNode representing the requested resource.
        @rtype: DrbNode
        @raise DrbFactoryException: if an error appear
        """
        # initialize current url (curl) and remaining segment path (path)
        pp = urlparse(url)
        if curl is None and path is None:
            if is_remote_url(pp):
                curl = f'{pp.scheme}://{pp.netloc}'
            path = pp.path.split('/')
            if curl is None:
                seg = path.pop(0)
                curl = f'/{seg}' if os.path.isabs(pp.path) else seg

        # try to create node from curl
        try:
            node = self.create(UrlNode(curl))
            for child in path:
                if child != '':
                    node = node[child, 1]
            return node
        except (DrbFactoryException, IndexError, KeyError, TypeError):
            if curl == url or len(path) == 0:
                raise DrbFactoryException(f'Cannot resolve URL: {url}')
            if is_remote_url(pp):
                seg = path.pop(0)
                # skip empty string (e.g. /path/to//data)
                if seg == '':
                    seg = path.pop(0)
                curl += f'/{seg}'
            else:
                curl = os.path.join(curl, path.pop(0))
            return self.__create_from_url(url, curl, path)

    def resolve(self, source: Union[str, DrbNode], **kwargs) \
            -> Tuple[DrbSignature, Optional[DrbNode]]:
        """Resolves the signature related to the passed source.

        :param source: source to be resolved
        :returns: Signature able to open the given source and the base node
        allowing to create the node via the resolved signature.
        :rtype: Tuple[DrbSignature, DrbNode]
        :raises:
            * DrbFactoryException when no factory matches this uri.
        """
        if isinstance(source, str):
            node = UrlNode(source)
        else:
            node = source
        protocol = None

        if node.parent is None:
            protocol = self.__retrieve_protocol(node)
            if protocol is None:
                raise DrbFactoryException(f'Cannot resolve: {source}')
            node = protocol.factory.create(node)

        container = self.__retrieve_container(node)
        if container is not None:
            node = container.factory.create(node)

        formatting = self.__retrieve_formatting(node)
        if formatting is not None:
            return formatting, node

        if container is None:
            if protocol is None:
                raise DrbFactoryException(f'Cannot resolve: {source}')
            return protocol, None
        return container, node

    def create(self, source: Union[DrbNode, str]) -> DrbNode:
        if isinstance(source, str):
            return self.__create_from_url(source)
        return super().create(source)


class DrbNodeList(list):
    def __init__(self, children: List[DrbNode]):
        super(DrbNodeList, self).__init__()
        self._list: List[DrbNode] = children
        self.resolver: DrbFactoryResolver = DrbFactoryResolver()

    def __resolve_node(self, node: DrbNode):
        try:
            return self.resolver.create(node)
        except DrbFactoryException:
            return node

    def __getitem__(self, item):
        result = self._list[item]
        if isinstance(result, DrbNode):
            return self.__resolve_node(result)
        else:
            return [self.__resolve_node(node) for node in result]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return DrbNodeListIterator(self._list.__iter__())

    def append(self, obj) -> None:
        raise DrbFactoryException

    def clear(self) -> None:
        raise DrbFactoryException

    def copy(self) -> List:
        raise DrbFactoryException

    def count(self, value) -> int:
        raise DrbFactoryException

    def insert(self, index: int, obj) -> None:
        raise DrbFactoryException

    def extend(self, iterable) -> None:
        raise DrbFactoryException

    def index(self, value, start: int = ..., __stop: int = ...) -> int:
        raise DrbFactoryException

    def pop(self, index: int = ...):
        raise DrbFactoryException

    def remove(self, value) -> None:
        raise DrbFactoryException

    def reverse(self) -> None:
        raise DrbFactoryException

    def sort(self, *, key: None = ..., reverse: bool = ...) -> None:
        raise DrbFactoryException

    def __eq__(self, other):
        raise DrbFactoryException

    def __ne__(self, other):
        raise DrbFactoryException

    def __add__(self, other):
        raise DrbFactoryException

    def __iadd__(self, other):
        raise DrbFactoryException

    def __radd__(self, other):
        raise DrbFactoryException

    def __setitem__(self, key, value):
        raise DrbFactoryException


class DrbNodeListIterator:
    def __init__(self, iterator):
        self.base_itr = iterator

    def __iter__(self):
        return self

    def __next__(self):
        node = next(self.base_itr)
        try:
            return DrbFactoryResolver().create(node)
        except DrbFactoryException:
            return node


def resolve_children(func):
    def inner(ref):
        if isinstance(ref, DrbNode) and func.__name__ == 'children':
            return DrbNodeList(func(ref))
        raise TypeError('@resolve_children decorator must be only apply on '
                        'children methods of a DrbNode')
    return inner
