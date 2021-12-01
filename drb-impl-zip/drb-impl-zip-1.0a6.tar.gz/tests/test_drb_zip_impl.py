import io
import os
import unittest
import zipfile
from pathlib import Path

from drb.exceptions import DrbNotImplementationException
from drb_impl_file import DrbFileAttributeNames, DrbFileFactory
from drb_impl_zip import DrbZipFactory
from drb_impl_zip.zip_node import DrbZipAttributeNames

SENTINEL_1_ROOT = "sentinel-1"

SENTINEL_1_MANIFEST_FAKE = "manifest_safe"
SENTINEL_1_SUPPORT = "support"


class TestDrbZip(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    zip_ok1 = current_path / "files" / "data-ok.zip"

    zip_s1 = current_path / "files" / "sentinel-1.zip"

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
        self.node = DrbZipFactory().create(self.node_file)
        return self.node

    def test_has_impl(self):
        node = self.open_node(str(self.zip_s1))

        first_node = node[0]
        node_manifest = first_node[SENTINEL_1_MANIFEST_FAKE, None, 1]
        self.assertTrue(node_manifest.has_impl(zipfile.ZipExtFile))
        self.assertTrue(node_manifest.has_impl(io.BufferedIOBase))
        node_support = first_node[SENTINEL_1_SUPPORT, None, 1]
        self.assertFalse(node_support.has_impl(zipfile.ZipExtFile))
        self.assertFalse(node_support.has_impl(io.BufferedIOBase))

    def test_get_impl_exception(self):
        node = self.open_node(str(self.zip_s1))

        first_node = node[0]

        node_support = first_node[SENTINEL_1_SUPPORT, None, 1]

        with self.assertRaises(DrbNotImplementationException):
            node_support.get_impl(io.BufferedIOBase)

        with self.assertRaises(DrbNotImplementationException):
            node_support.get_impl(zipfile.ZipExtFile)

    def test_get_impl(self):
        node = self.open_node(str(self.zip_s1))

        first_node = node[0]

        node_manifest = first_node[SENTINEL_1_MANIFEST_FAKE, None, 1]
        self.assertIsNotNone(node_manifest.get_impl(zipfile.ZipExtFile))

        impl = node_manifest.get_impl(zipfile.ZipExtFile)

        self.assertIsInstance(impl, zipfile.ZipExtFile)
        self.assertIsInstance(impl, io.BufferedIOBase)

        impl.close()
        first_node.close()

    def test_close(self):
        node = self.open_node(str(self.zip_s1))
        first_node = node[0]
        first_node.close()

    def test_get_impl_read_line(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_manifest = first_node[SENTINEL_1_MANIFEST_FAKE, None, 1]
        self.assertIsNotNone(node_manifest.get_impl(zipfile.ZipExtFile))

        impl = node_manifest.get_impl(zipfile.ZipExtFile)

        impl.readline()
        impl.readline()
        line3 = impl.readline()
        self.assertIn("<informationPackageMap>", str(line3))

        impl.close()

    def test_get_impl_read_buffer(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(node[0])

        first_node = node[0]

        node_manifest = first_node[SENTINEL_1_MANIFEST_FAKE, None, 1]
        self.assertIsNotNone(node_manifest.get_impl(zipfile.ZipExtFile))

        impl = node_manifest.get_impl(io.BufferedIOBase)

        impl.seek(588 + 40)

        buffer = impl.read(30)
        self.assertIn("<informationPackageMap>", str(buffer))

        print(impl.name)
        print(impl)

        impl.close()

    def test_file_has_impl(self):
        node = self.open_node(str(self.zip_s1))

        self.assertTrue(node.has_impl(io.BufferedIOBase))
        self.assertFalse(node.has_impl(zipfile.ZipExtFile))

    def test_get_file_impl(self):
        node = self.open_node(str(self.zip_s1))
        impl = node.get_impl(io.BufferedIOBase)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, io.BufferedIOBase)

        impl.close()

    def test_get_file_impl_exception(self):
        node = self.open_node(str(self.zip_s1))

        with self.assertRaises(DrbNotImplementationException):
            node.get_impl(zipfile.ZipExtFile)
