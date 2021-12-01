import os
import unittest
from drb.exceptions import DrbException
from drb_impl_file import DrbFileFactory
from drb_impl_file.drb_impl_file import DrbFileAttributeNames
from drb_impl_zip import DrbZipFactory

from pathlib import Path
from drb_impl_zip.zip_node import DrbZipAttributeNames

MY_DATA1_TXT = "mydata1.txt"
MY_DATA2_TXT = "mydata2.txt"

EMPTY_DIR = "empty_dir"

ROOT_DIR_DATA = "data"

MY_DATA_TXT = "mydata.txt"

SENTINEL_1_ROOT = "sentinel-1"


class TestDrbZip(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    zip_ok1 = current_path / "files" / "data-ok.zip"
    zip_ko1 = current_path / "files" / "data-nok.zip"

    zip_ok2 = current_path / "files" / "data-ok2.zip"
    zip_ko2 = current_path / "files" / "data-nok2.zip"
    zip_s1 = current_path / "files" / "sentinel-1.zip"
    zip_confused_names = current_path / "files" / "data-name-confused.zip"
    not_zip_files = current_path / "files" / "mydata.txt"

    zip_fake = current_path / "files" / "fake.zip"

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
        self.node = DrbZipFactory().create(self.node_file)
        return self.node

    def test_opened__file_node(self):
        node = self.open_node(str(self.zip_ok1))
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])

    def test_fake(self):
        node = self.open_node(str(self.zip_fake))

        self.assertEqual(node.name, "fake.zip")

        with self.assertRaises(DrbException):
            len(node)

    def test_open_URL_ok1(self):
        node = self.open_node(str(self.zip_ok1))
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1]
                             [MY_DATA_TXT, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][ROOT_DIR_DATA, None, 1]
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1]),
            1)

    def test_open_URL_ko1(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertEqual(len(node), 1)

        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])
        with self.assertRaises(KeyError):
            node[MY_DATA_TXT, None, 1]
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][ROOT_DIR_DATA, None, 1]
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1]
                             [MY_DATA_TXT, None, 1])

    def test_open_URL_ok2(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][MY_DATA_TXT, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][ROOT_DIR_DATA, None, 1]

        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 2]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1]),
            1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][MY_DATA_TXT, None, 1]),
            0)

        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                    EMPTY_DIR, None, 1]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                    EMPTY_DIR, None, 1]),
            2)
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1][MY_DATA1_TXT, None, 1])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1][MY_DATA2_TXT, None, 1])

    def test_open_URL_ko2(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][MY_DATA_TXT, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][ROOT_DIR_DATA, None, 1]

        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 2]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1]),
            1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][MY_DATA_TXT, None, 1]),
            0)

        self.assertEqual(
            len(node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                    EMPTY_DIR, None, 1]),
            2)
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1][MY_DATA1_TXT, None, 1])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1][MY_DATA2_TXT, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 1][EMPTY_DIR, None, 1][
                EMPTY_DIR, None, 1]["mydata3.txt", None, 1]

    def test_first_end_child(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertEqual(len(node), 1)
        self.assertIsNotNone(node[0])

        self.assertEqual(node[0].name, ROOT_DIR_DATA)
        self.assertEqual(node[-1].name, ROOT_DIR_DATA)

        self.assertEqual(node[0][0].name, EMPTY_DIR)
        self.assertEqual(node[0][-1].name, MY_DATA_TXT)

        with self.assertRaises(IndexError):
            node[0][-1][0]
        with self.assertRaises(IndexError):
            node[0][-1][-1]

        self.assertEqual(node[0][EMPTY_DIR, None, 1]
                         [0].name,
                         EMPTY_DIR)
        self.assertEqual(node[0][EMPTY_DIR, None, 1]
                         [-1].name,
                         EMPTY_DIR)

        self.assertEqual(
            node[0][0][-1]
            [0].name, MY_DATA1_TXT)
        self.assertEqual(
            node[0][0][-1]
            [-1].name, MY_DATA2_TXT)

    def test_get_named_child_without_occurrence(self):
        node = self.open_node(str(self.zip_ok2))

        list_occurrence = node[ROOT_DIR_DATA, None, 1][EMPTY_DIR]
        self.assertEqual(len(list_occurrence), 1)
        self.assertEqual(list_occurrence[0].name, EMPTY_DIR)
        list_occurrence_bis = list_occurrence[0][EMPTY_DIR]
        self.assertEqual(len(list_occurrence_bis), 1)
        self.assertEqual(list_occurrence_bis[0].name, EMPTY_DIR)

    def test_has_child(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())
        self.assertTrue(
            node[0][EMPTY_DIR, None, 1].has_child())
        self.assertTrue(
            node[0][EMPTY_DIR, None, 1]
            [EMPTY_DIR, None, 1].has_child())
        self.assertFalse(
            node[0][0][-1]
            [-1].has_child())

    def test_get_child_at(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())

        self.assertEqual(node[0][0].name, EMPTY_DIR)
        self.assertEqual(node[0][0][0][0].name, MY_DATA1_TXT)
        self.assertEqual(node[0][0][0][1].name, MY_DATA2_TXT)
        with self.assertRaises(IndexError):
            node[0][0][0][3]

        self.assertEqual(node[0][0][0]
                         [-1].name, MY_DATA2_TXT)

    def test_namespace_uri(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())
        self.assertIsNone(node[0].namespace_uri)

    def test_value_uri(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())
        self.assertIsNone(node[0].value)

    def test_test_namespace_uri_file(self):
        node = self.open_node(str(self.zip_ok1))

        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)
        self.assertEqual(node.name, self.node_file.name)

    def test_value_file(self):
        node = self.open_node(str(self.zip_ok1))

        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)
        self.assertEqual(node.value, self.node_file.value)

    def test_attributes_zip_files(self):
        node = self.open_node(str(self.zip_s1))

        list_attributes = node.attributes
        self.assertIn((DrbFileAttributeNames.DIRECTORY.value, None),
                      list_attributes.keys())
        self.assertIn((DrbFileAttributeNames.SIZE.value, None),
                      list_attributes.keys())
        self.assertEqual(node.get_attribute(
            DrbFileAttributeNames.DIRECTORY.value, None), False)

    def test_attributes(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(node[SENTINEL_1_ROOT, None, 1].attributes)
        list_attributes = node[SENTINEL_1_ROOT, None, 1].attributes
        self.assertIn((DrbZipAttributeNames.DIRECTORY.value, None),
                      list_attributes.keys())
        self.assertEqual(list_attributes[(DrbZipAttributeNames.DIRECTORY.value,
                                          None)], True)

        with self.assertRaises(KeyError):
            list_attributes[(DrbZipAttributeNames.DIRECTORY.value, 'toto')]

    def test_get_attribute(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(
            node[SENTINEL_1_ROOT, None, 1].get_attribute(DrbZipAttributeNames.
                                                         DIRECTORY.value))
        self.assertEqual(node[SENTINEL_1_ROOT, None, 1].
                         get_attribute(DrbZipAttributeNames.DIRECTORY.value),
                         True)

        self.assertEqual(node[SENTINEL_1_ROOT, None, 1]
                         ["manifest.safe", None, 1].
                         get_attribute(DrbZipAttributeNames.DIRECTORY.value),
                         False)

        self.assertEqual(node[SENTINEL_1_ROOT, None, 1]
                         ["manifest.safe", None, 1]
                         .get_attribute(DrbZipAttributeNames.SIZE.value),
                         14945)
        self.assertAlmostEqual(node[SENTINEL_1_ROOT, None, 1][
                                   "manifest.safe", None, 1].get_attribute(
            DrbZipAttributeNames.RATIO.value, None), 4.9, delta=0.1)
        self.assertAlmostEqual(node[SENTINEL_1_ROOT, None, 1]
                               ["manifest.safe", None, 1]
                               .get_attribute(DrbZipAttributeNames.PACKED.
                                              value),
                               3014, delta=10)
        self.assertEqual(node[SENTINEL_1_ROOT, None, 1]
                         ["measurement", None, 1].
                         get_attribute(DrbZipAttributeNames.SIZE.value),
                         0)
        self.assertEqual(node[SENTINEL_1_ROOT, None, 1]
                         ["measurement", None, 1].
                         get_attribute(DrbZipAttributeNames.RATIO.value),
                         0)
        self.assertEqual(node[SENTINEL_1_ROOT, None, 1]
                         ["measurement", None, 1].
                         get_attribute(DrbZipAttributeNames.PACKED.value),
                         0)

    def test_open_name_confused(self):
        node = self.open_node(str(self.zip_confused_names))

        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 1])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]

        first_node = node[ROOT_DIR_DATA, None, 1]
        self.assertEqual(len(first_node), 6)

        node_file = first_node[MY_DATA_TXT, None, 1]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)

        node_dir = first_node["mydata", None, 1]
        self.assertEqual(len(node_dir), 2)
        self.assertTrue(node_dir.has_child())

        node_dir = first_node["myd", None, 1]
        self.assertEqual(len(node_dir), 1)
        self.assertTrue(node_dir.has_child())

        node_dir = first_node["mydata_empty", None, 1]
        self.assertEqual(len(node_dir), 0)
        self.assertFalse(node_dir.has_child())

        node_file = first_node["my", None, 1]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)

        node_file = first_node["mydata_txt", None, 1]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)
        self.assertEqual(node_file.name, "mydata_txt")

    def test_parent(self):
        first_node = self.open_node(str(self.zip_ok2))

        self.assertEqual(first_node.parent, self.node_file.parent)
        self.assertEqual(first_node.value, self.node_file.value)

        first_child = first_node[0]
        self.assertEqual(first_child.parent, first_node)

    def test_path(self):
        first_node = self.open_node(str(self.zip_ok2))

        self.assertEqual(str(first_node.path.name), str(self.zip_ok2))

        first_child = first_node[0]
        path_child = str(self.zip_ok2) + '/' + first_child.name
        self.assertEqual(str(first_child.path.name), path_child)
