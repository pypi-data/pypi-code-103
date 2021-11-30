from typing import Optional, Any, List, Dict, Tuple

import drb
from drb import DrbItem, DrbNode
from drb.abstract_node import AbstractNode
from drb.events import Event
from drb.path import Path
from drb.predicat import Predicate


class DrbTestItem(DrbItem):
    def __init__(self, name: str, namespace_uri: str = None,
                 value: Any = None):
        self.changed = Event()
        self._name = name
        self._namespace_uri = namespace_uri
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name
        self.changed.notify(self, 'name', new_name)

    @property
    def namespace_uri(self) -> Optional[str]:
        return self._namespace_uri

    @namespace_uri.setter
    def namespace_uri(self, new_namespace_uri) -> None:
        self._namespace_uri = new_namespace_uri
        self.changed.notify(self, 'namespace_uri', new_namespace_uri)

    @property
    def value(self) -> Optional[Any]:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        self._value = new_value
        self.changed.notify(self, 'value', new_value)


class DrbTestNode(DrbTestItem, AbstractNode):
    def __init__(self, name: str, namespace_uri: str = None,
                 value: Any = None):
        super().__init__(name, namespace_uri, value)
        self._children = []

    @property
    def attributes(self) -> Dict[Tuple[str, str], DrbItem]:
        return {}

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def path(self) -> Path:
        pass

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        return self._children

    def get_attribute(self, name: str, namespace_uri: str = None) -> \
            Optional[DrbItem]:
        pass

    def has_child(self) -> bool:
        pass

    def insert_child(self, node: DrbNode, index: int) -> None:
        pass

    def append_child(self, node: DrbNode) -> None:
        self._children.append(node)

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


class DrbTestPredicate(Predicate):
    def matches(self, key) -> bool:
        return True
