import os
import posixpath
import unittest
from pathlib import Path
import io


from drb_impl_file import DrbFileFactory, DrbFileAttributeNames

from drb_impl_netcdf.netcdf_group_node import DrbNetcdfGroupNode
from drb_impl_netcdf.netcdf_node_factory import DrbNetcdfFactory, \
    DrbNetcdfNode

ROOT_GROUP = "root"
GROUP_NOT_EXIST = "fake_group"


class TestDrbNodeFactoryNetcdf(unittest.TestCase):
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

    def test_opened_file_node(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        self.assertIsInstance(node, DrbNetcdfNode)
        self.assertEqual(node.name, self.node_file.name)
        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)

    def test_base_node(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        self.assertEqual(node.parent, self.node_file.parent)
        self.assertEqual(node.value, self.node_file.value)

        self.assertIsInstance(node, DrbNetcdfNode)

        self.assertEqual(len(node), 1)
        self.assertTrue(node.has_child())

    def test_base_node_get_child(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        self.assertEqual(node[0].name, ROOT_GROUP)
        self.assertEqual(len(node.children), 1)

    def test_base_node_attribute(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        self.assertEqual(node.attributes, self.node_file.attributes)

        self.assertEqual(node.get_attribute(DrbFileAttributeNames.
                                            DIRECTORY.value),
                         self.node_file.get_attribute(DrbFileAttributeNames.
                                                      DIRECTORY.value))

    def test_base_node_impl(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        impl_base_file = io.BufferedIOBase

        self.assertTrue(node.has_impl(impl_base_file))

        impl = node.get_impl(impl_base_file)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, impl_base_file)

    def test_first_group(self):
        node = self.open_node(str(self.netcdf_with_one_group))
        root_node = node[0]

        self.assertIsInstance(root_node, DrbNetcdfGroupNode)
        self.assertEqual(root_node.name, ROOT_GROUP)

    def test_path(self):
        node = self.open_node(str(self.netcdf_with_one_group))

        root_node = node[0]

        self.assertEqual(root_node.path.path, node.path.path + posixpath.sep
                         + 'root')
