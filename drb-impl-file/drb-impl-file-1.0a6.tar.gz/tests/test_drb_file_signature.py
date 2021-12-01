import os
import sys
import unittest
from drb.factory import DrbFactoryResolver
from drb.utils.logical_node import DrbLogicalNode

from drb.exceptions import DrbFactoryException


class TestDrbFileFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)

        cls.mock_package_path = os.path.abspath(
            os.path.join(path, 'resources'))
        sys.path.append(cls.mock_package_path)

        cls.resolver = DrbFactoryResolver()

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(cls.mock_package_path)

    def test_resolve_ok(self):
        node = DrbLogicalNode('.')
        signature, node_resolved = self.resolver.resolve(node)
        self.assertEqual(signature.label, 'file')

    def test_resolve_fails(self):
        node = DrbLogicalNode('https://gitlab.com/drb-python')
        with self.assertRaises(DrbFactoryException):
            self.resolver.resolve(node)
