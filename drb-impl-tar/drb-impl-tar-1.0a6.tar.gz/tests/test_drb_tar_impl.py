import io
import os
import unittest
import zipfile
from pathlib import Path
from tarfile import ExFileObject

from drb.exceptions import DrbNotImplementationException
from drb_impl_file import DrbFileFactory
from drb_impl_tar import DrbTarFactory

SENTINEL_1_ROOT = "sentinel-1"

SENTINEL_1_MANIFEST = "manifest.safe"
SENTINEL_1_SUPPORT = "support"


class TestDrbZip(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    tar_test = current_path / "files" / "test.tar"
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

    def test_has_impl(self):
        node = self.open_node(str(self.tar_test))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_dir_xml = first_node["xml"][0]

        node_file_xml_1 = node_dir_xml["a_xml", None, 1]

        self.assertTrue(node_file_xml_1.has_impl(ExFileObject))

        self.assertTrue(node_file_xml_1.has_impl(io.BufferedIOBase))

        self.assertFalse(node_file_xml_1.has_impl(io.BufferedReader))

        self.assertFalse(node_dir_xml.has_impl(ExFileObject))

        self.assertFalse(node_dir_xml.has_impl(io.BufferedIOBase))

    def test_get_impl_exception(self):
        node = self.open_node(str(self.tar_test))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_dir_xml = first_node['xml'][0]

        with self.assertRaises(DrbNotImplementationException):
            node_dir_xml.get_impl(io.BufferedIOBase)
        with self.assertRaises(DrbNotImplementationException):
            node_dir_xml.get_impl(ExFileObject)

        node_file_xml_1 = node_dir_xml["a_xml", None, 1]
        with self.assertRaises(DrbNotImplementationException):
            node_file_xml_1.get_impl(io.BufferedReader)

    def test_get_impl(self):
        node = self.open_node(str(self.tar_test))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_dir_xml = first_node['xml'][0]

        node_file_1 = node_dir_xml["a_xml", None, 1]

        self.assertIsNotNone(node_file_1.get_impl(ExFileObject))

        impl = node_file_1.get_impl(ExFileObject)

        self.assertIsInstance(impl, ExFileObject)
        self.assertIsInstance(impl, io.BufferedIOBase)

        impl.close()

    def test_get_impl_read_line(self):
        node = self.open_node(str(self.tar_test))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_dir_xml = first_node["xml"][0]

        node_file_xml_1 = node_dir_xml["a_xml"][0]

        self.assertIsNotNone(node_file_xml_1.get_impl(ExFileObject))

        impl = node_file_xml_1.get_impl(io.BufferedIOBase)

        impl.readline()
        impl.readline()
        impl.readline()

        line4 = impl.readline()
        self.assertIn("XML1!!", str(line4))

        impl.close()

    def test_get_impl_read_buffer(self):
        node = self.open_node(str(self.tar_test))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_dir_xml = first_node['xml'][0]

        node_file_xml_1 = node_dir_xml["a_xml", None, 1]

        self.assertIsNotNone(node_file_xml_1.get_impl(ExFileObject))

        impl = node_file_xml_1.get_impl(ExFileObject)

        impl.seek(20)

        buffer = impl.read(10)
        self.assertIn("XML1!!", str(buffer))

        impl.close()

    def test_file_has_impl(self):
        node = self.open_node(str(self.tar_test))

        self.assertTrue(node.has_impl(io.BufferedIOBase))

        self.assertFalse(node.has_impl(zipfile.ZipExtFile))

    def test_get_file_impl(self):
        node = self.open_node(str(self.tar_test))

        impl = node.get_impl(io.BufferedIOBase)

        self.assertIsNotNone(impl)

        self.assertIsInstance(impl, io.BufferedIOBase)
        impl.close()

    def test_get_file_impl_exception(self):
        node = self.open_node(str(self.tar_test))

        with self.assertRaises(DrbNotImplementationException):
            node.get_impl(zipfile.ZipExtFile)
