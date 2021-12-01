import os
import io
import unittest
from pathlib import Path


import netCDF4
from drb.exceptions import DrbNotImplementationException, DrbException
from drb_impl_file import DrbFileFactory

from drb_impl_netcdf import DrbNetcdfFactory, DrbNetcdfAttributeNames
from drb_impl_netcdf.netcdf_common import NAMESPACE_NETCDF_NODE

GROUP_ROOT = "root"
GROUP_ONE = "mozaic_flight_2012030319051051_descent"
GROUP_TWO = "mozaic_flight_2012030403540535_ascent"

GROUP_NOT_EXIST = "fake_group"


class TestDrbListNodeNetcdf(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    netcdf_with_one_group = current_path / "files" / 'sgpsondewnpnC1.nc'

    def setUp(self) -> None:
        self.node = None
        self.node_file = None

    def tearDown(self) -> None:
        if self.node is not None:
            self.node.close()
        if self.node_file is not None:
            self.node_file.close()

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbNetcdfFactory().create(self.node_file)
        return self.node

    def test_list_children(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        self.assertTrue(dim_list.has_child())

    def test_list_get_named_children(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]
        dim_list = root_node[("dimensions", 1)]

        self.assertIsNotNone(dim_list[("time", 1)])
        with self.assertRaises(KeyError):
            dim_list[("time", 2)]

        list_children = dim_list["time"]
        self.assertEqual(list_children[0].name, 'time')

    def test_list_children_get_at(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        self.assertEqual(len(dim_list), 1)

        self.assertIsNotNone(dim_list[0])
        self.assertIsNotNone(dim_list[-1])

        with self.assertRaises(IndexError):
            dim_list[2]

        with self.assertRaises(KeyError):
            dim_list["toto"]

        self.assertEqual(dim_list[0], dim_list[-1])

        self.assertEqual(len(dim_list.children), 1)
        self.assertTrue(dim_list.has_child())

    def test_list_parent(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]
        dim_list = root_node[("dimensions", 1)]
        self.assertEqual(dim_list.parent, root_node)
        self.assertEqual(dim_list.name, "dimensions")

    def test_list_namespace_uri(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        self.assertEqual(dim_list.namespace_uri, NAMESPACE_NETCDF_NODE)

    def test_list_value(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        self.assertIsNone(dim_list.value)

    def test_list_impl_not_supported(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        self.assertFalse(dim_list.has_impl(io.BufferedIOBase))
        self.assertFalse(dim_list.has_impl(netCDF4.Dimension))

        with self.assertRaises(DrbNotImplementationException):
            dim_list.get_impl(io.BufferedIOBase)

    def test_list_no_attributes(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]
        self.assertFalse(bool(dim_list.attributes))
        with self.assertRaises(DrbException):
            dim_list.get_attribute(DrbNetcdfAttributeNames.UNLIMITED.value,
                                   None)
