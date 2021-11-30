import unittest

from drb.utils.url_node import UrlNode
from drb.exceptions import DrbException
from .utils import DrbTestPredicate


class TestUrlNode(unittest.TestCase):
    node = UrlNode('https://gael-systems.com/path/to/data')

    def test_namespace_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_name(self):
        self.assertEqual('data', self.node.name)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_path(self):
        self.assertEqual('/path/to/data', self.node.path.path)

    def test_parent(self):
        self.assertIsNone(self.node.parent)

    def test_attributes(self):
        self.assertEqual({}, self.node.attributes)

    def test_get_attribute(self):
        with self.assertRaises(DrbException):
            self.node.get_attribute('test')

    def test_children(self):
        self.assertEqual([], self.node.children)

    def test_has_child(self):
        self.assertFalse(self.node.has_child())

    def test_has_impl(self):
        self.assertFalse(self.node.has_impl(str))

    def test_get_impl(self):
        with self.assertRaises(DrbException):
            self.node.get_impl(str)

    def test_getitem(self):
        node = None
        with self.assertRaises(DrbException):
            node = self.node[0]
        with self.assertRaises(DrbException):
            node = self.node['foo']
        with self.assertRaises(DrbException):
            node = self.node['foo', 'bar']
        with self.assertRaises(DrbException):
            node = self.node['foo', 1]
        with self.assertRaises(DrbException):
            node = self.node['foo', 'bar', 1]
        with self.assertRaises(DrbException):
            node = self.node[DrbTestPredicate()]

    def test_truediv(self):
        node = None
        with self.assertRaises(DrbException):
            node = self.node / 'foo'
        with self.assertRaises(DrbException):
            node = self.node / ('foo', 'bar')
        with self.assertRaises(DrbException):
            node = self.node / ('foo', 1)
        with self.assertRaises(DrbException):
            node = self.node / ('foo', 'bar', 1)
        with self.assertRaises(DrbException):
            node = self.node / ('foo', 'bar')
        with self.assertRaises(DrbException):
            node = self.node / DrbTestPredicate()

    def test_len(self):
        self.assertEqual(0, len(self.node))

    def test_insert_child(self):
        with self.assertRaises(NotImplementedError):
            self.node.insert_child(0, UrlNode('test'))

    def test_append_child(self):
        with self.assertRaises(NotImplementedError):
            self.node.append_child(UrlNode('test'))

    def test_replace_child(self):
        with self.assertRaises(NotImplementedError):
            self.node.replace_child(0, UrlNode('test'))

    def test_remove_child(self):
        with self.assertRaises(NotImplementedError):
            self.node.remove_child(0)

    def test_add_attribute(self):
        with self.assertRaises(NotImplementedError):
            self.node.add_attribute('test', False)

    def test_remove_attribute(self):
        with self.assertRaises(NotImplementedError):
            self.node.remove_attribute('test')

    def test_close(self):
        self.node.close()
