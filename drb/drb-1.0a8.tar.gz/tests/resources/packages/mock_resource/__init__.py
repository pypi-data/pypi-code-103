import uuid
from typing import Any, Optional, List, Dict, Tuple

import drb
from drb import DrbNode, AbstractNode
from drb.exceptions import DrbException
from drb.factory import DrbSignature, DrbFactory, DrbSignatureType
from drb.path import ParsedPath
from drb.utils.logical_node import DrbLogicalNode


class MockResourceNode(AbstractNode):
    def __init__(self, node: DrbNode):
        self._node = node

    @property
    def name(self) -> str:
        return self._node.name

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
        child = DrbLogicalNode('sub', parent=self)
        sub_child = DrbLogicalNode('path', parent=child)
        sub_sub_child = DrbLogicalNode('foobar.data', parent=sub_child)
        child.append_child(sub_child)
        sub_child.append_child(sub_sub_child)
        return [child]

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


class MockResourceFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return MockResourceNode(node)


class MockResourceSignature(DrbSignature):
    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('1008f81c-4bb7-11ec-81d3-0242ac130003')

    @property
    def label(self) -> str:
        return 'MockResource'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return MockResourceFactory()

    def match(self, node: DrbNode) -> bool:
        return node.name.endswith('.rs')
