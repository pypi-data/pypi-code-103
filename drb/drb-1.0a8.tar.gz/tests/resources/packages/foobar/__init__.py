import uuid
from typing import Optional, Any, List, Dict, Tuple

from drb import DrbNode
from drb.abstract_node import AbstractNode
from drb.factory import DrbFactory, DrbSignature, DrbSignatureType
from drb.path import Path


class DrbFoobarNode(AbstractNode):
    def __init__(self, name):
        self._name = f'Foobar_{name}'

    @property
    def name(self) -> str:
        return self._name

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
        pass

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def children(self) -> List[DrbNode]:
        return []

    @property
    def path(self) -> Optional[Path]:
        return None

    def has_child(self) -> bool:
        pass

    def insert_child(self, node: DrbNode, index: int) -> None:
        pass

    def append_child(self, node: DrbNode) -> None:
        pass

    def replace_child(self, index: int, new_node: DrbNode) -> None:
        pass

    def remove_child(self, index: int) -> None:
        pass

    def add_attribute(self, name: str, value: Optional[Any] = None,
                      namespace_uri: Optional[str] = None) -> None:
        pass

    def remove_attribute(self, name: str, namespace_uri: str = None) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type) -> Any:
        return None

    def close(self) -> None:
        pass


class DrbFoobarFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return DrbFoobarNode(node.path.filename)


class FoobarSignature(DrbSignature):
    def __init__(self):
        self._factory = DrbFoobarFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('75eddcbc-2752-11ec-9621-0242ac130002')

    @property
    def label(self) -> str:
        return 'foobar'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.PROTOCOL

    @property
    def factory(self) -> DrbFactory:
        return self._factory

    def match(self, node: DrbNode) -> bool:
        return 'foobar' == node.path.scheme
