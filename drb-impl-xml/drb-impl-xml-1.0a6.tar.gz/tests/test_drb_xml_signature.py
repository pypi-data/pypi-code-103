import os
import sys
import unittest
from pathlib import Path

from drb.factory import DrbFactoryResolver
from drb.utils.logical_node import DrbLogicalNode

from drb.exceptions import DrbFactoryException
import tempfile


class TestDrbImageSignature(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    tar_test = current_path / "files" / "test.tar"

    empty_file = current_path / "files" / "empty.file"
    path = None
    fake_path = None

    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)

        cls.mock_package_path = os.path.abspath(
            os.path.join(path, 'resources'))
        sys.path.append(cls.mock_package_path)

        cls.resolver = DrbFactoryResolver()

        fd, cls.path = tempfile.mkstemp(suffix='.xml', text=True)
        fd, cls.fake_path = tempfile.mkstemp(suffix='.file', text=True)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(cls.mock_package_path)
        os.remove(cls.path)
        os.remove(cls.fake_path)

    def test_resolve_ok(self):
        node = DrbLogicalNode(self.path)
        signature, node_resolved = self.resolver.resolve(node)
        self.assertEqual(signature.label, 'xml')

    def test_resolve_no_tar(self):
        node = DrbLogicalNode(self.fake_path)
        try:
            signature, node_resolved = self.resolver.resolve(node)
            self.assertNotEqual(signature.label, 'xml')
        except DrbFactoryException:
            pass
