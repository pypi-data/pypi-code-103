import sys
import unittest
import os

from drb import DrbNode
from drb.utils.logical_node import DrbLogicalNode
from drb.predicat import Predicate


class MyPredicate(Predicate):
    def matches(self, node: DrbNode) -> bool:
        return 'a' == node.namespace_uri


class TestDrbNode(unittest.TestCase):
    mock_package_path = None
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.mock_package_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'packages'))
        sys.path.append(cls.mock_package_path)

        cls.node = DrbLogicalNode(os.getcwd())
        cls.node.append_child(DrbLogicalNode('data1.zip'))
        cls.node.append_child(DrbLogicalNode('data1.zip', namespace_uri='a'))
        cls.node.append_child(DrbLogicalNode('data2.txt'))
        cls.node.append_child(DrbLogicalNode('data2.txt'))
        cls.node.append_child(DrbLogicalNode('data2.txt', namespace_uri='b'))

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(cls.mock_package_path)

    def test_getitem_int(self):
        node = self.node[1]
        self.assertEqual('data1.zip', node.name)
        self.assertEqual('a', node.namespace_uri)
        self.assertEqual("<class 'zip.ZipNode'>", str(node.__class__))

    def test_getitem_slice(self):
        self.skipTest('Does not support slice yet: node[1:3]')

    def test_getitem_str(self):
        data = self.node['data2.txt']
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))
        self.assertEqual("<class 'txt.TextNode'>", str(data[1].__class__))

    def test_getitem_tuple(self):
        data = self.node['data2.txt', ]
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))
        self.assertEqual("<class 'txt.TextNode'>", str(data[1].__class__))

        data = self.node['data2.txt', 'b']
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))

        data = self.node['data2.txt', 1]
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'txt.TextNode'>", str(data.__class__))

        data = self.node['data1.zip', 'a', 1]
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'zip.ZipNode'>", str(data.__class__))

        data = self.node['data1.zip', None, 1]
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'zip.ZipNode'>", str(data.__class__))

    def test_getitem_predicate(self):
        data = self.node[MyPredicate()]
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual("<class 'zip.ZipNode'>", str(data[0].__class__))

    def test_truediv_str(self):
        data = self.node / 'data2.txt'
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))
        self.assertEqual("<class 'txt.TextNode'>", str(data[1].__class__))

    def test_truediv_tuple(self):
        self.skipTest("Does not support tuple yet: node / ('name', 'ns', 2)")
        data = self.node / ('data2.txt',)
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))
        self.assertEqual("<class 'txt.TextNode'>", str(data[1].__class__))

        data = self.node / 'data2.txt', 'b'
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual("<class 'txt.TextNode'>", str(data[0].__class__))

        data = self.node / 'data2.txt', 1
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'txt.TextNode'>", str(data.__class__))

        data = self.node / 'data1.zip', 'a', 1
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'zip.ZipNode'>", str(data.__class__))

        data = self.node / 'data1.zip', None, 1
        self.assertIsInstance(data, DrbNode)
        self.assertEqual("<class 'zip.ZipNode'>", str(data.__class__))

    def test_truediv_predicate(self):
        data = self.node / MyPredicate()
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))
        self.assertEqual("<class 'zip.ZipNode'>", str(data[0].__class__))
