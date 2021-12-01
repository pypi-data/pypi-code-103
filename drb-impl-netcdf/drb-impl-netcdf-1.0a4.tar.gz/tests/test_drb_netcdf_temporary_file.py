import os
import unittest
from pathlib import Path

from drb.exceptions import DrbException
from drb_impl_file import DrbFileFactory
from drb_impl_netcdf.netcdf_common import NAMESPACE_NETCDF_NODE

from drb_impl_netcdf.netcdf_group_node import DrbNetcdfGroupNode
from drb_impl_netcdf.netcdf_node_factory import DrbNetcdfFactory
from drb_impl_zip import DrbZipFactory

GROUP_ROOT = "root"
GROUP_ONE = "mozaic_flight_2012030319051051_descent"
GROUP_TWO = "mozaic_flight_2012030403540535_ascent"


class TestDrbGroupNodeNetcdf(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    zip_with_one_group = current_path / "files" / 'sgpsondewnpnC1.zip'
    name_netcdf_with_one_group = 'sgpsondewnpnC1.nc'

    def setUp(self) -> None:
        self.node = None
        self.node_file = None

    def tearDown(self) -> None:
        if self.node is not None:
            self.node.close()
        if self.node_zip is not None:
            self.node_zip.close()
        if self.node_file is not None:
            self.node_file.close()

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)

        self.node_zip = DrbZipFactory().create(self.node_file)
        self.node = DrbNetcdfFactory().create(self.node_zip[0])
        return self.node

    def test_first_group(self):

        node = self.open_node(str(self.zip_with_one_group))

        root_node = node[0]

        self.assertIsInstance(root_node, DrbNetcdfGroupNode)
        self.assertEqual(root_node.name, GROUP_ROOT)
        self.assertEqual(root_node.namespace_uri, NAMESPACE_NETCDF_NODE)

    def test_only_one_group(self):
        node = self.open_node(str(self.zip_with_one_group))

        root_node = node[0]

        self.assertTrue(root_node.has_child())
        self.assertEqual(len(root_node), 2)

        self.assertIsNotNone(root_node[0])
        self.assertEqual(root_node[0].name, "dimensions")

        self.assertIsNotNone(root_node[-1])
        self.assertEqual(root_node[-1].name, "variables")

        with self.assertRaises(IndexError):
            root_node[3]
