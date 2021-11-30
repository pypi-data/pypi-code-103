from typing import Any, Optional, List, Dict, Tuple, Union

from ..node import DrbNode
from ..path import ParsedPath, Path, parse_path
from ..exceptions import DrbException


class UrlNode(DrbNode):
    """
    URL node is a simple implementation of DrbNode base on a given URL without
    any attribute or child. This node must be use only in this core library
    (drb) and not in any implementation. It's mainly uses to generate the root
    node generated from an URI.
    """
    def __init__(self, source: Union[str, Path, ParsedPath]):
        self._path = parse_path(source)

    @property
    def name(self) -> str:
        return self._path.filename

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException('UrlNode has no attribute')

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self._path

    @property
    def children(self) -> List[DrbNode]:
        return []

    def has_child(self) -> bool:
        return False

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type) -> Any:
        raise DrbException('Url node does not support any implementation')

    def insert_child(self, index: int, node: DrbNode) -> None:
        raise NotImplementedError

    def append_child(self, node: DrbNode) -> None:
        raise NotImplementedError

    def replace_child(self, index: int, new_node: DrbNode) -> None:
        raise NotImplementedError

    def remove_child(self, index: int) -> None:
        raise NotImplementedError

    def add_attribute(self, name: str, value: Optional[Any] = None,
                      namespace_uri: Optional[str] = None) -> None:
        raise NotImplementedError

    def remove_attribute(self, name: str, namespace_uri: str = None) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass

    def __len__(self):
        return 0

    def __getitem__(self, item):
        raise DrbException('UrlNode has no child')

    def __truediv__(self, child):
        raise DrbException('UrlNode has no child')
