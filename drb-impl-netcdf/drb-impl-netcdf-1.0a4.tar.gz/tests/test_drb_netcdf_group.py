import io
import os
import unittest
from pathlib import Path

import netCDF4
from drb.exceptions import DrbNotImplementationException, DrbException
from drb_impl_file import DrbFileFactory
from drb_impl_netcdf.netcdf_common import NAMESPACE_NETCDF_NODE

from drb_impl_netcdf.netcdf_group_node import DrbNetcdfGroupNode
from drb_impl_netcdf.netcdf_node_factory import DrbNetcdfFactory

GROUP_ROOT = "root"
GROUP_ONE = "mozaic_flight_2012030319051051_descent"
GROUP_TWO = "mozaic_flight_2012030403540535_ascent"

GROUP_NOT_EXIST = "fake_group"


class TestDrbGroupNodeNetcdf(unittest.TestCase):
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

    def test_first_group(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        self.assertIsInstance(root_node, DrbNetcdfGroupNode)
        self.assertEqual(root_node.name, GROUP_ROOT)
        self.assertEqual(root_node.namespace_uri, NAMESPACE_NETCDF_NODE)

    def test_only_one_group(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        self.assertTrue(root_node.has_child())
        self.assertEqual(len(root_node), 2)

        self.assertIsNotNone(root_node[0])
        self.assertEqual(root_node[0].name, "dimensions")

        self.assertIsNotNone(root_node[-1])
        self.assertEqual(root_node[-1].name, "variables")

        with self.assertRaises(IndexError):
            root_node[3]

    def test_only_group_with_sub_group(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]

        self.assertTrue(root_node.has_child())
        self.assertTrue(len(root_node) > 2)

        self.assertIsNotNone(root_node[(GROUP_ONE, 1)])
        self.assertIsNotNone(root_node[GROUP_ONE])
        list_group_one = root_node[GROUP_ONE]
        self.assertEqual(list_group_one[0].name, GROUP_ONE)

        with self.assertRaises(KeyError):
            root_node[(GROUP_ONE, 2)]

        self.assertIsNotNone(root_node[(GROUP_TWO, 1)])
        with self.assertRaises(KeyError):
            root_node[(GROUP_TWO, 2)]

    def test_multiples_sub_group(self):
        node = self.open_node(str(self.netcdf_with_sample_groups))

        root_node = node[0]
        level_node_1 = root_node[("Test_Drb_Group_A", 1)]
        self.assertIsNotNone(level_node_1)
        level_node_2 = level_node_1[("Test_Drb_Sub_Group_A1", 1)]
        self.assertIsNotNone(level_node_2)

    def test_group_attributes(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]
        list_attributes = root_node.attributes

        self.assertEqual(len(list_attributes), 27)

        self.assertEqual(list_attributes[('phase_fitting_1', None)],
                         'Phase fitting length is  60 s from   0 min to'
                         ' 120 min\r\n')

        with self.assertRaises(KeyError):
            list_attributes[('phase_fitting_1', 'test')]

        self.assertEqual(root_node.get_attribute('zeb_platform'),
                         'sgpsondewnpnC1.a1')

    def test_group_attributes_sub_grp(self):
        node = self.open_node(str(self.netcdf_with_sample_groups))

        root_node = node[0]
        list_attributes = root_node.attributes

        self.assertEqual(len(list_attributes), 0)

        level_node_1 = root_node[("Test_Drb_Group_A", 1)]
        list_attributes = level_node_1.attributes

        self.assertEqual(len(list_attributes), 2)
        self.assertEqual(level_node_1.get_attribute('first_attribute'),
                         'attributes test A')

        level_node_2 = level_node_1[("Test_Drb_Sub_Group_A1", 1)]

        list_attributes = level_node_2.attributes

        self.assertEqual(len(list_attributes), 2)
        self.assertEqual(level_node_2.get_attribute('first_attribute'),
                         'attributes test A1')

        level_node_2b = level_node_1[("Test_Drb_Sub_Group_A2", 1)]

        list_attributes = level_node_2b.attributes

        self.assertEqual(len(list_attributes), 2)
        self.assertEqual(level_node_2b.get_attribute('first_attribute'),
                         'attributes test B')

        level_node_1b = root_node[-1]
        list_attributes = level_node_1b.attributes
        self.assertEqual(len(list_attributes), 0)

        level_node_2b = level_node_1b[("Test_Drb_Sub_Group_B1", 1)]

        self.assertEqual(level_node_2b.get_attribute('first_attribute'),
                         'attributes test B1')

    def test_group_parent(self):
        node = self.open_node(str(self.netcdf_with_sample_groups))

        root_node = node[0]

        self.assertEqual(root_node.parent, node)
        level1 = root_node[0]

        self.assertEqual(level1.parent, root_node)

    def test_group_value(self):
        node = self.open_node(str(self.netcdf_with_sample_groups))

        root_node = node[0]

        self.assertIsNone(root_node.value)

    def test_group_get_children_at(self):
        node = self.open_node(str(self.netcdf_with_sample_groups))

        root_node = node[0]
        list_attributes = root_node.attributes

        self.assertEqual(len(list_attributes), 0)

        level_node_1 = root_node[0]
        self.assertIsNotNone(level_node_1)
        self.assertEqual(level_node_1.name, "Test_Drb_Group_A")

        with self.assertRaises(IndexError):
            root_node[5]
        self.assertEqual(root_node[-2], root_node[len(root_node) - 2])

    def test_group_impl(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))

        root_node = node[0]
        first_child = root_node[(GROUP_ONE, 1)]

        self.assertTrue(first_child.has_impl(netCDF4.Dataset))

        netcdf_dataset = first_child.get_impl(netCDF4.Dataset)

        self.assertIsInstance(netcdf_dataset, netCDF4.Dataset)

    def test_dimension_impl_not_supported(self):
        node = self.open_node(str(self.netcdf_with_multiple_groups))
        root_node = node[0]

        self.assertIsInstance(root_node, DrbNetcdfGroupNode)
        self.assertFalse(root_node.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbNotImplementationException):
            root_node.get_impl(io.BufferedIOBase)
