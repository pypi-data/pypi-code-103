import os
import sys
import unittest
from pathlib import Path

from drb.factory import DrbFactoryResolver
from drb.utils.logical_node import DrbLogicalNode

from drb.exceptions import DrbFactoryException


class TestDrbZipSignature(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    zip_ok2 = current_path / "files" / "data-ok2.zip"
    not_zip_files = current_path / "files" / "mydata.txt"

    zip_case = current_path / "files" / "mydata.Zip"

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
        node = DrbLogicalNode(self.zip_ok2)
        signature, node_resolved = self.resolver.resolve(node)
        self.assertEqual(signature.label, 'zip')

    def test_resolve_uppercase_ok(self):
        node = DrbLogicalNode(self.zip_case)
        signature, node_resolved = self.resolver.resolve(node)
        self.assertEqual(signature.label, 'zip')

    def test_resolve_no_zip(self):
        node = DrbLogicalNode(self.not_zip_files)
        try:
            signature, node_resolved = self.resolver.resolve(node)
            self.assertNotEqual(signature.label, 'zip')
        except DrbFactoryException:
            pass
