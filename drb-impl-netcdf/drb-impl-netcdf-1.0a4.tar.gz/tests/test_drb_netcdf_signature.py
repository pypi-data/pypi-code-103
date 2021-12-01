import os
import sys
import unittest
from pathlib import Path

from drb.factory import DrbFactoryResolver
from drb.utils.logical_node import DrbLogicalNode

from drb.exceptions import DrbFactoryException


class TestDrbNetcdfSignature(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    netcdf_with_one_group = current_path / "files" / 'sgpsondewnpnC1.nc'
    empty_file = current_path / "files" / "empty.file"

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
        node = DrbLogicalNode(self.netcdf_with_one_group)
        signature, node = self.resolver.resolve(node)
        self.assertEqual(signature.label, 'netcdf')

    def test_resolve_no_tar(self):
        node = DrbLogicalNode(self.empty_file)
        try:
            signature, node = self.resolver.resolve(node)
            self.assertNotEqual(signature.label, 'netcdf')
        except DrbFactoryException:
            pass
