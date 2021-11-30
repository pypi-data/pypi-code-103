import abc
import unittest
from typing import Optional, Any, Union, List, Dict, Tuple

from drb import DrbItem, DrbNode
from drb.abstract_node import AbstractNode
from drb.mutable_node import MutableNode
from drb.node_impl import NodeImpl
from drb.path import ParsedPath
from drb.factory.factory import DrbFactory
from drb.predicat import Predicate


class DrbItemTest(DrbItem):
    @property
    def name(self) -> Optional[str]:
        return super().name

    @property
    def namespace_uri(self) -> Optional[str]:
        return super().namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return super().value


class DrbNodeImplTest(NodeImpl):
    def has_impl(self, impl: type) -> bool:
        return super().has_impl(impl)

    def get_impl(self, impl: type) -> Any:
        return super().get_impl(impl)


class PredicateTest(Predicate):
    def matches(self, key) -> bool:
        return super().matches(key)


class DrbFactoryTest(DrbFactory):
    def _create(self, node: Union[DrbNode, str, Any]) -> DrbNode:
        return super(DrbFactoryTest, self)._create(node)


class AbstractNodeTest(DrbNodeImplTest, AbstractNode, abc.ABC):
    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return super(AbstractNodeTest, self).get_attribute(name, namespace_uri)

    def has_child(self) -> bool:
        return super(AbstractNodeTest, self).has_child()

    def close(self) -> None:
        super(AbstractNodeTest, self).close()


class DrbNodeTest(AbstractNodeTest, DrbItemTest):
    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return super().attributes

    @property
    def parent(self) -> Optional[DrbNode]:
        return super(DrbNodeTest, self).parent

    @property
    def path(self) -> ParsedPath:
        return super(DrbNodeTest, self).path

    @property
    def children(self) -> List[DrbNode]:
        return super(DrbNodeTest, self).children


class DrbMutableTest(MutableNode, DrbNodeTest):

    def _init_attributes(self):
        pass

    def _init_children(self):
        pass

    def insert_child(self, index: int, node: DrbNode) -> None:
        super(DrbMutableTest, self).insert_child(index, node)

    def append_child(self, node: DrbNode) -> None:
        super(DrbMutableTest, self).append_child(node)

    def replace_child(self, index: int, new_node: DrbNode) -> None:
        super(DrbMutableTest, self).replace_child(index, new_node)

    def remove_child(self, index: int) -> None:
        super(DrbMutableTest, self).remove_child(index)

    def add_attribute(self, name: str, value: Optional[Any] = None,
                      namespace_uri: Optional[str] = None) -> None:
        super(DrbMutableTest, self).add_attribute(name, value, namespace_uri)

    def remove_attribute(self, name: str, namespace_uri: str = None) -> None:
        super(DrbMutableTest, self).remove_attribute(name, namespace_uri)


class TestEvent(unittest.TestCase):
    def test_abstract_drb_item(self):
        item = DrbItemTest()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(item.name, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(item.namespace_uri, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(item.value, None)

    def test_abstract_node_impl(self):
        impl = DrbNodeImplTest()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(impl.get_impl(str), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(impl.has_impl(str), None)

    def test_abstract_drb_node(self):
        node = DrbNodeTest()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.attributes, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.get_attribute("aa"), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.parent, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.path, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.children, None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.has_child(), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.close(), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node[0], None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(len(node), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node/'test', None)

    def test_mutable_node(self):
        node = DrbMutableTest()

        self.assertIsNone(node.name)
        node.name = 'test'
        self.assertEqual('test', node.name)

        self.assertIsNone(node.namespace_uri)
        node.namespace_uri = 'https://gael-systems.com'
        self.assertEqual('https://gael-systems.com', node.namespace_uri)

        self.assertIsNone(node.value)
        node.value = False
        self.assertEqual(False, node.value)

        path = ParsedPath('test')
        self.assertIsNone(node.path)
        node.path = path
        self.assertEqual(path, node.path)

        parent = DrbMutableTest()
        parent.path = ParsedPath('parent')
        self.assertIsNone(node.parent)
        node.parent = parent
        self.assertEqual(parent, node.parent)

        attributes = {('attr', None): True}
        self.assertIsNone(node.attributes)
        node.attributes = attributes
        self.assertEqual(attributes, node.attributes)

        children = [DrbMutableTest()]
        self.assertIsNone(node.children)
        node.children = children
        self.assertEqual(children, node.children)

        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.append_child(DrbNodeTest()), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.insert_child(0, DrbNodeTest()), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.replace_child(0, DrbNodeTest()), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.remove_child(0), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.add_attribute("None", None, None), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.remove_attribute("None", None), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(node.replace_child(0, DrbNodeTest()), None)

    def test_abstract_factory(self):
        factory = DrbFactoryTest()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(factory.create('uri=None'), None)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(factory.create(DrbNodeTest()), None)

    def test_predicate(self):
        predicate = PredicateTest()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(predicate.matches('no'), None)
