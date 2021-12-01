import os
import posixpath
import unittest
from pathlib import Path

from drb.exceptions import DrbException
from drb_impl_file import DrbFileFactory
from drb_impl_file.drb_impl_file import DrbFileAttributeNames
from drb_impl_tar.execptions import DrbTarNodeException
from drb_impl_tar.file_tar_node import DrbTarFactory
from drb_impl_tar.tar_node import DrbTarAttributeNames

T__V_T___T__DBL = "S2__OPER_AUX_ECMWFD_PDMC_20190216T120000_" \
                  "V20190217T090000_20190217T210000.DBL"

LONG_DIR = "veryveryveryveryveryveryveryveryveryveryveryveryveryvery" \
           "veryveryveryveryveryveryLongDir"

T____ANNOTATION_DAT = "S2A_OPER_PRD_HKTM___20191121T080247_20191121T080252" \
                      "_0001_annotation.dat"

T____SAFE = "S2A_OPER_PRD_HKTM___20191121T080247_20191121T080252_0001.SAFE"

T__HDR_XML = "S2__OPER_AUX_ECMWFD_PDMC_20190216T120000_V20190217T090000_" \
             "20190217T210000.HDR.xml"


class TestDrbZipFactory(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    tar_test = current_path / "files" / "test.tar"
    tar_gnu = current_path / "files" / "gnu.tar"
    tar_old_gnu = current_path / "files" / "oldgnu.tar"
    tar_posix = current_path / "files" / "posix.tar"
    tar_ustar = current_path / "files" / "ustar.tar"
    tar_v7 = current_path / "files" / "v7.tar"
    tar_file_long_names = current_path / "files" / "test_long_file.tar"
    tar_absolute_path = current_path / "files" / "test_absolute_path.tar"
    tar_relative_path = current_path / "files" / "test_relative_path.tar"
    tar_confuse_name = current_path / "files" / "tar_with_confuse_names.tar"
    tar_fake = current_path / "files" / "fake.tar"
    node = None
    node_file = None

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
        self.node = DrbTarFactory().create(self.node_file)
        return self.node

    def check_test_tar(self, node):
        self.assertTrue(node.has_child())

        self.assertIsNotNone(node['test'][0])
        self.assertIsNotNone(node['test'][0]['empty.file'][0])
        self.assertIsNotNone(node['test'][0]['not-empty.file'][0])
        self.assertIsNotNone(node['test'][0]["a"][0])
        self.assertIsNotNone(node['test'][0]["a"][0]["aaa.txt"][0])

        with self.assertRaises(KeyError):
            node['test'][0]["aa"][0]
            node['test'][0]["a"][0]["aaa.tx"][0]

        self.assertIsNotNone(node['test'][0]["b"][0]["bbb.txt"][0])

        with self.assertRaises(KeyError):
            node['test'][0]["a"][0]["bbb.tx"][0]
            node['test'][0]["b"][0]["aaa.tx"][0]

    def test_opened_file_node(self):
        node = self.open_node(str(self.tar_test))
        self.assertEqual(node.name, "test.tar")

        self.check_test_tar(node)

    def test_fake(self):
        node = self.open_node(str(self.tar_fake))

        self.assertEqual(node.name, "fake.tar")

        with self.assertRaises(DrbTarNodeException):
            len(node)

    def test_confuse_name(self):
        node = self.open_node(str(self.tar_confuse_name))

        self.check_test_tar(node)

        self.assertEqual(node[0]._tar_info.name, "test")

        self.assertEqual(len(node['test'][0]), 8)

        self.assertIsNotNone(node['test'][0]["xm"][0])
        self.assertFalse(node['test'][0]["xm"][0].has_child())
        self.assertTrue(node['test'][0]["xml"][0].has_child())

        self.assertEqual(len(node['test'][0]["xml"][0]), 2)

        self.assertIsNotNone(node['test'][0]["not-empty", None, 1])
        with self.assertRaises(KeyError):
            node['test'][0]["not-empty", None, 2]
        self.assertFalse(node['test'][0]["not-empty"][0].has_child())

        self.assertEqual(node[0]._tar_info.name, "test")

    def test_absolute_path(self):
        node = self.open_node(str(self.tar_absolute_path))

        self.assertTrue(node.has_child())

        self.assertEqual(node[0].name, "test")
        self.assertEqual(node[0]._tar_info.name, "/tmp/test")

    def test_relative_path(self):
        node = self.open_node(str(self.tar_relative_path))

        self.assertTrue(node.has_child())

        self.assertEqual(node[0].name, "test")
        self.assertEqual(node[0]._tar_info.name, "tmp/test")

        self.check_test_tar(node)

    def chack_small_name_tar(self, first_node):
        self.assertTrue(first_node.has_child())
        self.assertIsNotNone(
            first_node["SMALL_NAME"])
        node = first_node["SMALL_NAME"][0]
        self.assertIsNotNone(node[T__HDR_XML][0])
        self.assertIsNotNone(node[T__V_T___T__DBL, None, 1])

        with self.assertRaises(KeyError):
            node[(T__V_T___T__DBL, None, 2)]

        # TODO mix XML and Tar ....
        # node_xml = node.get_named_child(
        # "S2__OPER_AUX_ECMWFD_PDMC_20190216T120000_V20190217T090000"
        # "_20190217T210000.HDR.xml", occurrence=1)
        # self.assertIsNotNone(node_xml.get_named_child(
        # "Earth_Explorer_Header", occurrence=1))

        self.assertEqual(len(node), 2)

        list_node = node[T__HDR_XML]
        self.assertEqual(len(list_node), 1)
        self.assertEqual(list_node[0].name,
                         T__HDR_XML)

    def test_gnu_tar(self):
        first_node = self.open_node(str(self.tar_gnu))

        self.chack_small_name_tar(first_node)

    def test_old_gnu_tar(self):
        first_node = self.open_node(str(self.tar_old_gnu))

        self.chack_small_name_tar(first_node)

    def test_posix_tar(self):
        first_node = self.open_node(str(self.tar_posix))

        self.chack_small_name_tar(first_node)

    def test_ustar_tar(self):
        first_node = self.open_node(str(self.tar_ustar))

        self.chack_small_name_tar(first_node)

    def test_v7_tar(self):
        first_node = self.open_node(str(self.tar_v7))

        self.chack_small_name_tar(first_node)

    def test_file_long_names(self):
        first_node = self.open_node(str(self.tar_file_long_names))

        self.assertIsNotNone(first_node[T____SAFE][0])
        node = first_node[T____SAFE][0]

        self.assertIsNotNone(node[T____ANNOTATION_DAT][0])

        self.assertIsNotNone(first_node[T____SAFE][0])

        node = first_node[T____SAFE][0]

        for index in range(2):
            self.assertIsNotNone(node[LONG_DIR][0])
            node = node[LONG_DIR][0]
            self.assertEqual(node.name, LONG_DIR)

        # self.assertIsNotNone(node.get_named_child("manifest.safe",
        #                                          occurrence=1))

    def test_value(self):
        node = self.open_node(str(self.tar_test))

        self.assertTrue(node[0].has_child())

        self.assertIsNone(node[0].value)

    def test_namespace_uri(self):
        node = self.open_node(str(self.tar_test))

        self.assertTrue(node[0].has_child())

        self.assertIsNone(node[0].namespace_uri)

    def test_namespace_uri_file(self):
        node = self.open_node(str(self.tar_test))

        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)
        self.assertEqual(node.name, self.node_file.name)

    def test_value_file(self):
        node_file = DrbFileFactory().create(str(self.tar_test))
        node = DrbTarFactory().create(node_file)

        self.assertEqual(node.namespace_uri, node_file.namespace_uri)
        self.assertEqual(node.value, node_file.value)

    def test_attributes(self):
        first_node = self.open_node(str(self.tar_test))

        node_dir_xml = first_node['test'][0]['xml'][0]

        list_attributes = node_dir_xml.attributes

        self.assertIn((DrbTarAttributeNames.DIRECTORY.value, None),
                      list_attributes.keys())

        self.assertEqual(list_attributes[(DrbTarAttributeNames.DIRECTORY.value,
                                          None)], True)

        with self.assertRaises(KeyError):
            list_attributes[(DrbTarAttributeNames.DIRECTORY.value, 'test')]

    def test_get_attribute(self):
        node = self.open_node(str(self.tar_test))

        node_dir_xml = node['test'][0]['xml'][0]

        self.assertEqual(node_dir_xml.
                         get_attribute(DrbTarAttributeNames.SIZE.value), 0)

        self.assertEqual(node_dir_xml.
                         get_attribute(DrbTarAttributeNames.DIRECTORY.value),
                         True)

        self.assertIn("2017", node_dir_xml.
                      get_attribute(DrbTarAttributeNames.MODIFIED.value))
        self.assertIn("14", node_dir_xml.
                      get_attribute(DrbTarAttributeNames.MODIFIED.value))

        node_a_xml = node_dir_xml["a_xml"][0]

        self.assertEqual(node_a_xml.
                         get_attribute(DrbTarAttributeNames.SIZE.value), 44)

        self.assertEqual(node_a_xml.
                         get_attribute(DrbTarAttributeNames.DIRECTORY.value),
                         False)

    def test_attributes_zip_files(self):
        node = self.open_node(str(self.tar_test))

        list_attributes = node.attributes

        self.assertIn((DrbFileAttributeNames.DIRECTORY.value, None),
                      list_attributes.keys())

        self.assertIn((DrbFileAttributeNames.SIZE.value, None),
                      list_attributes.keys())

        self.assertEqual(node.get_attribute(
            DrbFileAttributeNames.DIRECTORY.value, None), False)

    def test_parent(self):
        first_node = self.open_node(str(self.tar_test))

        self.assertEqual(first_node.parent, self.node_file.parent)
        self.assertEqual(first_node.value, self.node_file.value)

        first_child = first_node[0]
        self.assertEqual(first_child.parent, first_node)

        first_child.close()

    def test_path(self):
        first_node = self.open_node(str(self.tar_test))

        self.assertEqual(first_node.path.path, str(self.tar_test))

        node_dir_xml = first_node['test'][0]['xml'][0]
        self.assertEqual(node_dir_xml.path.path, str(self.tar_test) +
                         posixpath.sep + 'test' + posixpath.sep + "xml")
