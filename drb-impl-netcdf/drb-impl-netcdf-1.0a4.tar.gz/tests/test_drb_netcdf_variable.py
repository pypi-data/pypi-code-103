import io
import os
import unittest
from pathlib import Path

import netCDF4
import numpy
from drb.exceptions import DrbNotImplementationException, DrbException
from drb_impl_file import DrbFileFactory

from drb_impl_netcdf.netcdf_common import DrbNetcdfSimpleValueNode, \
    NAMESPACE_NETCDF_NODE
from drb_impl_netcdf.netcdf_node_factory import DrbNetcdfFactory

GROUP_ROOT = "root"
GROUP_ONE = "mozaic_flight_2012030319051051_descent"
GROUP_TWO = "mozaic_flight_2012030403540535_ascent"

GROUP_NOT_EXIST = "fake_group"


class TestDrbVaraibleNodeNetcdf(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    netcdf_fake = current_path / "files" / "fake.nc"
    netcdf_with_one_group = current_path / "files" / 'sgpsondewnpnC1.nc'
    netcdf_with_multiple_groups = current_path / "files" / 'test_hgroups.nc'
    netcdf_with_sample_groups = current_path / "files" / 'sample.nc'

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

    def test_variable_dimension_shape(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]
        self.assertIsNotNone(var_air_press)

        list_dim = var_air_press[('dimensions', 1)]
        self.assertIsNotNone(list_dim)
        self.assertIn('recNum', list_dim.value)

        list_shape = var_air_press['shape'][0]
        self.assertIsInstance(list_shape, DrbNetcdfSimpleValueNode)
        self.assertIn(74, list_shape.value)

    def test_variable_attributes(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_air_press = list_var[('rh', 1)]
        self.assertIsNotNone(var_air_press)

        attributes = var_air_press.attributes
        self.assertEqual(len(attributes), 4)

        self.assertIsNotNone(var_air_press.get_attribute('units', None))
        attr = var_air_press.get_attribute('units', None)
        self.assertEqual(attr, '%')
        attr = var_air_press.get_attribute('missing_value', None)
        self.assertEqual(attr, -9999.0)

        with self.assertRaises(DrbException):
            self.assertIsNotNone(var_air_press.get_attribute('toto', None))

    def test_variable_parent(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]

        self.assertEqual(var_air_press.parent, list_var)

    def test_variable_impl(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]

        self.assertTrue(var_air_press.has_impl(netCDF4.Variable))

        impl = var_air_press.get_impl(netCDF4.Variable)

        self.assertIsInstance(impl, netCDF4.Variable)

    def test_variable_impl_masked_array(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]

        self.assertTrue(var_air_press.has_impl(numpy.ma.masked_array))

        impl = var_air_press.get_impl(numpy.ma.masked_array)

        self.assertIsInstance(impl, numpy.ma.masked_array)
        self.assertIsInstance(impl, numpy.ma.core.MaskedArray)
        self.assertIsInstance(impl, numpy.ndarray)

        impl = var_air_press.get_impl(numpy.ndarray)

        self.assertEqual(impl[9], 85338)

        var_air_press.close()

    def test_variable_impl_not_supported(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]

        self.assertFalse(var_air_press.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbNotImplementationException):
            var_air_press.get_impl(io.BufferedIOBase)

    def test_variable_namespace_uri(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        group_two = root_node[GROUP_TWO]
        list_var = group_two[0][('variables', 1)]

        var_air_press = list_var[('air_press', 1)]

        self.assertEqual(var_air_press.namespace_uri, NAMESPACE_NETCDF_NODE)

    def test_variable_get_first_last_children(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_wind = list_var[('u_wind', 1)]

        first_child_node = var_wind[0]
        self.assertIsNotNone(first_child_node)

        self.assertEqual(first_child_node.name, 'dimensions')

        lest_child_node = var_wind[-1]
        self.assertIsNotNone(lest_child_node)
        self.assertEqual(lest_child_node.name, 'size')

    def test_variable_scalar(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_base_time = list_var[('base_time', 1)]

        self.assertIsNotNone(var_base_time)
        self.assertEqual(len(var_base_time), 1)

        with self.assertRaises(KeyError):
            var_base_time[('dimensions', 1)]

        self.assertEqual(var_base_time.value, 1020770640)

        self.assertTrue(var_base_time.has_impl(netCDF4.Variable))

        self.assertFalse(var_base_time.has_impl(numpy.ma.masked_array))

    def test_variable_not_scalar(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_lon = list_var[('lon', 1)]

        self.assertIsNotNone(var_lon)
        self.assertEqual(len(var_lon), 3)

        dimensions_node = var_lon[('dimensions', 1)]
        self.assertIsNotNone(dimensions_node)
        self.assertEqual(len(dimensions_node.value), 1)
        self.assertEqual(dimensions_node.value[0], 'time')

        shape_node = var_lon['shape'][0]
        self.assertIsNotNone(shape_node)
        self.assertEqual(len(shape_node.value), 1)
        self.assertEqual(shape_node.value[0], 2951)

        self.assertEqual(var_lon.value, None)

    def test_variable_simple_get_children(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_lon = list_var[('lon', 1)]
        dimensions_node = var_lon['dimensions'][0]
        self.assertIsNotNone(dimensions_node)
        with self.assertRaises(IndexError):
            dimensions_node[0]

        with self.assertRaises(IndexError):
            dimensions_node[-1]

            dimensions_node[0]

    def test_variable_simple_attributes(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_lon = list_var[('lon', 1)]
        self.assertTrue(var_lon.has_child())
        dimensions_node = var_lon[('dimensions', 1)]

        self.assertEqual(len(dimensions_node.attributes), 0)
        with self.assertRaises(DrbException):
            dimensions_node.get_attribute('units', None)

    def test_variable_has_not_impl(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        list_var = root_node[('variables', 1)]

        var_lon = list_var[('lon', 1)]
        dimensions_node = var_lon['dimensions'][0]

        self.assertFalse(dimensions_node.has_impl(io.BufferedIOBase))
        self.assertFalse(dimensions_node.has_impl(netCDF4.Variable))

        with self.assertRaises(DrbNotImplementationException):
            dimensions_node.get_impl(netCDF4.Variable)
