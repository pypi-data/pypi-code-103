import io
import os
import shutil
import unittest
import tempfile

from drb.exceptions import DrbException, DrbNotImplementationException
from drb_impl_file import DrbFileNode, DrbFileAttributeNames


def random_content_file(path: str) -> None:
    """
    Generates a drb_impl_file with a random binary array.
    """
    with open(path, 'wb') as file:
        file.write(bytearray(os.urandom(1000)))


def generate_test_data() -> str:
    """
    Generates following temporary directories and files:
    root
    |-- a
    |   |-- aa
    |   |-- ab
    |   |-- ac
    |-- b
    :return: root path
    """
    root_path = tempfile.mkdtemp()
    random_content_file(os.path.join(root_path, '.b'))
    os.makedirs(os.path.join(root_path, 'a'), mode=0o744)
    random_content_file(os.path.join(root_path, 'a', 'aa'))
    random_content_file(os.path.join(root_path, 'a', 'ab'))
    random_content_file(os.path.join(root_path, 'a', 'ac'))
    return root_path


class TestDrbFileNode(unittest.TestCase):
    test_path: str = None

    @classmethod
    def setUpClass(cls) -> None:
        TestDrbFileNode.test_path = generate_test_data()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TestDrbFileNode.test_path)

    def test_check_class(self):
        self.assertTrue(issubclass(DrbFileNode, DrbFileNode))

    def test_name(self):
        node = DrbFileNode(self.test_path)
        self.assertEqual(os.path.basename(self.test_path), node.name)

    def test_namespace_uri(self):
        node = DrbFileNode(self.test_path)
        self.assertIsNone(node.namespace_uri)

    def test_value(self):
        path = self.test_path
        self.assertIsNone(DrbFileNode(path).value)
        path = os.path.join(self.test_path, 'a', 'ab')
        self.assertIsNone(DrbFileNode(path).value)

    def test_parent(self):
        node = DrbFileNode(self.test_path)
        self.assertIsNone(node.parent)
        child = node.children[0]
        self.assertEqual(node, child.parent)

    def test_attributes(self):
        path = os.path.join(self.test_path, '.b')
        file_stat = os.stat(path)
        node = DrbFileNode(path)
        attributes = node.attributes

        key = (DrbFileAttributeNames.DIRECTORY.value, None)
        self.assertEqual(attributes[key], False)

        key = (DrbFileAttributeNames.SIZE.value, None)
        self.assertEqual(attributes[key], file_stat.st_size)

        key = (DrbFileAttributeNames.MODIFIED.value, None)
        self.assertEqual(attributes[key], file_stat.st_mtime)

        key = (DrbFileAttributeNames.READABLE.value, None)
        self.assertEqual(attributes[key], True)

        key = (DrbFileAttributeNames.WRITABLE.value, None)
        self.assertEqual(attributes[key], True)

        key = (DrbFileAttributeNames.HIDDEN.value, None)
        self.assertEqual(attributes[key], True)

        self.assertEqual(len(attributes.keys()), 6)

    def test_children(self):
        node = DrbFileNode(self.test_path)
        self.assertEqual(2, len(node.children))
        self.assertEqual('.b', node.children[0].name)
        self.assertEqual('a', node.children[1].name)

    def test_get_attribute(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        self.assertTrue(
            node.get_attribute(DrbFileAttributeNames.DIRECTORY.value))

        node = DrbFileNode(os.path.join(self.test_path, '.b'))
        self.assertFalse(
            node.get_attribute(DrbFileAttributeNames.DIRECTORY.value))

        with self.assertRaises(DrbException):
            node.get_attribute('foobar')

    def test_has_child(self):
        node = DrbFileNode(self.test_path)
        self.assertTrue(node.has_child())
        node = DrbFileNode(os.path.join(self.test_path, '.b'))
        self.assertFalse(node.has_child())

    def test_get_children_count(self):
        node = DrbFileNode(self.test_path)
        self.assertEqual(2, len(node))
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        self.assertEqual(3, len(node))
        node = DrbFileNode(os.path.join(self.test_path, 'a', 'ac'))
        self.assertEqual(0, len(node))

    def test_get_named_child(self):
        parent_node = DrbFileNode(os.path.join(self.test_path, 'a'))
        node = parent_node['ab'][0]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, DrbFileNode)
        self.assertEqual('ab', node.name)

        node = parent_node['ab']
        self.assertIsNotNone(node)
        self.assertIsInstance(node, list)
        self.assertEqual(1, len(node))
        self.assertEqual('ab', node[0].name)

        with self.assertRaises(KeyError):
            parent_node['ab', 'https://foobar.org/foo', 0]
        with self.assertRaises(KeyError):
            self.assertListEqual(parent_node['foobar'])
        with self.assertRaises(KeyError):
            parent_node['foobar'][0]

    def test_get_first_child(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        first = node[0]
        self.assertEqual('aa', first.name)

    def test_get_last_child(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        last = node[-1]
        self.assertEqual('ac', last.name)

    def test_get_child_at(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        child = node[0]
        self.assertEqual('aa', child.name)
        child = node[1]
        self.assertEqual('ab', child.name)
        child = node[2]
        self.assertEqual('ac', child.name)
        with self.assertRaises(IndexError):
            node[3]
        child = node[-1]
        self.assertEqual('ac', child.name)
        child = node[-2]
        self.assertEqual('ab', child.name)
        with self.assertRaises(IndexError):
            node[-4]

    def test_has_impl(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a'))
        self.assertFalse(node.has_impl(io.RawIOBase))
        self.assertFalse(node.has_impl(io.FileIO))
        self.assertFalse(node.has_impl(io.BufferedIOBase))
        self.assertFalse(node.has_impl(io.BufferedReader))
        self.assertFalse(node.has_impl(str))

        node = node['ac'][0]
        self.assertTrue(node.has_impl(io.RawIOBase))
        self.assertTrue(node.has_impl(io.FileIO))
        self.assertTrue(node.has_impl(io.BufferedIOBase))
        self.assertTrue(node.has_impl(io.BufferedReader))
        self.assertFalse(node.has_impl(dict))

    def test_get_impl(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a', 'ac'))
        with node.get_impl(io.RawIOBase) as stream:
            self.assertTrue(isinstance(stream, io.FileIO))
        with node.get_impl(io.FileIO) as stream:
            self.assertTrue(isinstance(stream, io.FileIO))
        with node.get_impl(io.BufferedIOBase) as stream:
            self.assertTrue(isinstance(stream, io.BufferedReader))
        with node.get_impl(io.BufferedReader) as stream:
            self.assertTrue(isinstance(stream, io.BufferedReader))
        with self.assertRaises(DrbNotImplementationException):
            node.get_impl(list)

    def test_close(self):
        node = DrbFileNode(os.path.join(self.test_path, 'a', 'ac'))
        # Shall not raise any exception: Silent close.
        node.close()

    def test_path_uri(self):
        path_expected = os.path.join(self.test_path, 'a', 'ac')
        node = DrbFileNode(path_expected)

        self.assertIsNotNone(node.path)

        print(node.path)

        self.assertEqual(node.path.path, str(path_expected))
        node.close()
