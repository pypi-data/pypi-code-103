import uuid
from typing import Any, Optional, List, Dict, Tuple

import drb
from drb import DrbNode, AbstractNode
from drb.exceptions import DrbException
from drb.factory import DrbSignature, DrbFactory, DrbSignatureType
from drb.path import ParsedPath


class MockDataNode(AbstractNode):
    def __init__(self, node: DrbNode):
        self._node = node

    @property
    def name(self) -> str:
        return self._node.name[:-5]

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._node.parent

    @property
    def path(self) -> ParsedPath:
        return self._node.path / self.name

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        return []

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException

    def has_child(self) -> bool:
        return True

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type) -> Any:
        raise DrbException


class MockDataFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return MockDataNode(node)


class MockResourceSignature(DrbSignature):
    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('e727af50-4c3e-11ec-81d3-0242ac130003')

    @property
    def label(self) -> str:
        return 'MockData'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.FORMATTING

    @property
    def factory(self) -> DrbFactory:
        return MockDataFactory()

    def match(self, node: DrbNode) -> bool:
        return node.name.endswith('.data')
