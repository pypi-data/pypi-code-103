import io
import os
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


class TestDrbDimensionNodeNetcdf(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    netcdf_fake = current_path / "files" / "fake.nc"
    netcdf_with_one_group = current_path / "files" / 'sgpsondewnpnC1.nc'
    netcdf_with_multiple_groups = current_path / "files" / 'test_hgroups.nc'

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

    def test_dimension_unlimited(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]
        self.assertIsNotNone(dim_list[("time", 1)])

        dim_time = dim_list[("time", 1)]
        self.assertEqual(dim_time.value, -1)

        list_attribute = dim_time.attributes
        self.assertEqual(
            list_attribute[(DrbNetcdfAttributeNames.UNLIMITED.value, None)],
            True)

        self.assertTrue(dim_time.get_attribute(
            DrbNetcdfAttributeNames.UNLIMITED.value, None))

    def test_dimension_limited(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        first_group = root_node[('mozaic_flight_2012030319051051_descent', 1)]

        dim_list = first_group[("dimensions", 1)]
        self.assertIsNotNone(dim_list[("air_press", 1)])

        dim_time = dim_list[("air_press", 1)]
        self.assertEqual(dim_time.value, 78)

        list_attribute = dim_time.attributes
        self.assertEqual(
            list_attribute[(DrbNetcdfAttributeNames.UNLIMITED.value, None)],
            False)

        self.assertFalse(dim_time.get_attribute(
            DrbNetcdfAttributeNames.UNLIMITED.value, None))

    def test_dimension_no_children(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        dim_time = dim_list[("time", 1)]

        with self.assertRaises(IndexError):
            dim_time[0]

        with self.assertRaises(KeyError):
            dim_time["toto"]

        self.assertEqual(len(dim_time.children), 0)
        self.assertFalse(dim_time.has_child())
        self.assertEqual(len(dim_time), 0)

    def test_dimension_parent(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        dim_time = dim_list[0]

        self.assertEqual(dim_time.parent, dim_list)

        self.assertEqual(dim_time.name, "time")

    def test_dimension_impl(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        dim_time = dim_list[("time", 1)]

        self.assertTrue(dim_time.has_impl(netCDF4.Dimension))

        dim_nc = dim_time.get_impl(netCDF4.Dimension)

        self.assertIsInstance(dim_nc, netCDF4.Dimension)

    def test_dimension_impl_not_supported(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        dim_time = dim_list[("time", 1)]

        self.assertFalse(dim_time.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbNotImplementationException):
            dim_time.get_impl(io.BufferedIOBase)

    def test_dimension_namespace_uri(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        dim_list = root_node[("dimensions", 1)]

        dim_time = dim_list[("time", 1)]

        self.assertEqual(dim_time.namespace_uri, NAMESPACE_NETCDF_NODE)
