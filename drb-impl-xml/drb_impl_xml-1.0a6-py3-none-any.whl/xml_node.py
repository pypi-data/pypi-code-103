import re
from typing import Optional, Any, Union, List, Dict, Tuple

import drb
from typing.io import IO
from xml.etree.ElementTree import parse, Element
from io import BufferedIOBase, RawIOBase

from drb import DrbNode
from drb.abstract_node import AbstractNode
from drb.path import ParsedPath
from drb.exceptions import DrbNotImplementationException, DrbException


def extract_namespace_name(value: str) -> Tuple[str, str]:
    """
    Extracts namespace and name from a tag of a Element
    :param value: XML element tag
    :type value: str
    :return: a tuple containing the extracted namespace and name
    :rtype: tuple
    """
    ns, name = re.match(r'({.*})?(.*)', value).groups()
    if ns is not None:
        ns = ns[1:-1]
    return ns, name


class XmlNode(AbstractNode):

    def __init__(self, element: Element, parent: DrbNode = None, **kwargs):
        namespace_uri, name = extract_namespace_name(element.tag)
        self._name = name
        self._namespace_uri = namespace_uri
        self._parent = parent
        self._attributes = None
        self._children = None
        self._elem: Element = element
        self._path = None
        if 'path' in kwargs.keys() and isinstance(kwargs['path'], ParsedPath):
            self._path = kwargs['path'] / name

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self._namespace_uri

    @property
    def value(self) -> Optional[Any]:
        if self.has_child():
            return None
        return self._elem.text

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            if self._parent is None:
                self._path = ParsedPath(f'/{self._name}')
            else:
                self._path = self.parent.path / self.name
        return self._path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            for k, v in self._elem.attrib.items():
                ns, name = extract_namespace_name(k)
                self._attributes[(name, ns)] = v
        return self._attributes

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = [XmlNode(e, self) for e in list(self._elem)]
        return self._children

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: int = None) -> \
            Union[DrbNode, List[DrbNode]]:
        try:
            ns = {}
            tag = name
            if namespace_uri is not None:
                ns = {'ns': namespace_uri}
                tag = f'ns:{name}'
            found = self._elem.findall(tag, ns)
            if len(found) > 0:
                if occurrence is None:
                    return [XmlNode(e, parent=self) for e in found]
                if occurrence > 0:
                    return XmlNode(found[occurrence - 1], parent=self)
            raise DrbException(f'Child ({name},{namespace_uri},{occurrence}) '
                               f'not found')
        except (IndexError, TypeError) as error:
            raise DrbException(f'Child ({name},{namespace_uri},{occurrence}) '
                               f'not found') from error

    def has_impl(self, impl: type) -> bool:
        return impl == str and not self.has_child()

    def get_impl(self, impl: type) -> Any:
        if self.has_impl(impl):
            return self.value
        raise DrbNotImplementationException(
            f"XmlNode doesn't implement {impl}")

    def close(self) -> None:
        pass

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        try:
            return self.attributes[name, namespace_uri]
        except KeyError:
            raise DrbException(f'No attribute ({name}:{namespace_uri}) found!')

    def has_child(self) -> bool:
        return len(self) > 0


class XmlBaseNode(AbstractNode):

    def __init__(self, node: DrbNode,
                 source: Union[BufferedIOBase, RawIOBase, IO]):
        """
        The given source is closed via this class #close() method.
        """
        self.base_node = node
        self.source = source
        xml_root = parse(source).getroot()
        self.xml_node = XmlNode(xml_root, parent=self, path=node.path)

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    @property
    def children(self) -> List[DrbNode]:
        return [self.xml_node]

    def has_child(self) -> bool:
        return True

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type) -> Any:
        return self.base_node.get_impl(impl)

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: int = None) -> Union[DrbNode,
                                                          List[DrbNode]]:
        try:
            if self.xml_node.name == name and \
                    self.xml_node.namespace_uri == namespace_uri:
                if occurrence is None:
                    return [self.xml_node]
                elif occurrence == 1:
                    return self.xml_node
            raise DrbException(f'Child ({name},{occurrence}) not found')
        except (IndexError, TypeError) as error:
            raise DrbException(f'Child ({name},{occurrence}) not found') \
                from error

    def close(self) -> None:
        if self.source:
            self.source.close()
        # TBC: shall the base node be closes by base node creator (?)
        self.base_node.close()
