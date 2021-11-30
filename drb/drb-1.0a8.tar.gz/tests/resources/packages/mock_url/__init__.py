import uuid
from typing import Any, Optional, List, Dict, Tuple, Union

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbException
from drb.factory import DrbSignature, DrbFactory, DrbSignatureType
from drb.path import ParsedPath


class MockUrlNode(AbstractNode):
    def __init__(self, source):
        if isinstance(source, DrbNode):
            self._path = source.path
        else:
            raise DrbException

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

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self._path

    @property
    def children(self) -> List[DrbNode]:
        return []

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException

    def has_child(self) -> bool:
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type) -> Any:
        raise DrbException


class MockUrlFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return MockUrlNode(node)


class MockUrlSignature(DrbSignature):
    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('aa51e438-4ba8-11ec-81d3-0242ac130003')

    @property
    def label(self) -> str:
        return 'MockUrl'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.PROTOCOL

    @property
    def factory(self) -> DrbFactory:
        return MockUrlFactory()

    def match(self, node: DrbNode) -> bool:
        return node.path.scheme == 'mockurl' or \
               node.path.scheme.startswith('/mockurl')
