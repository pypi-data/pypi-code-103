from typing import Any, List, Dict, Optional, Tuple

import drb

from drb import DrbNode
from drb.exceptions import DrbNotImplementationException, DrbException
from drb.path import ParsedPath

from drb_impl_netcdf.netcdf_common import DrbNetcdfAbstractNode


class DrbNetcdfListNode(DrbNetcdfAbstractNode):

    def __init__(self, parent: DrbNode, name: str):
        self._name = name
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = []
        self._path = None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            self._path = self.parent.path / self.name
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        return self._children

    def has_child(self) -> bool:
        return len(self.children) > 0

    def append_child(self, node: DrbNode) -> None:
        self._children.append(node)

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type) -> Any:
        raise DrbNotImplementationException(f'no {impl} implementation found')
