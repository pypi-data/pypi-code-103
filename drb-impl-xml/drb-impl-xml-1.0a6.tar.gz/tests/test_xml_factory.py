import unittest
import os
import tempfile

from drb_impl_xml import XmlNodeFactory, XmlBaseNode
from drb_impl_file import DrbFileNode


class TestXmlFactoryNode(unittest.TestCase):
    xml = """
    <fb:foobar xmlns:fb="https://foobar.org/foobar"
               xmlns:f="https://foobar.org/foo"
               xmlns:b="https://foobar.org/bar">
        <f:foo>3</f:foo>
        <b:bar>Hello</b:bar>
    </fb:foobar>
    """
    path = None
    invalid_path = None
    file_node = None

    @classmethod
    def setUpClass(cls) -> None:
        fd, cls.path = tempfile.mkstemp(suffix='.xml', text=True)
        with os.fdopen(fd, 'w') as file:
            file.write(cls.xml)
            file.flush()
        cls.file_node = DrbFileNode(cls.path)
        fd, cls.invalid_path = tempfile.mkstemp(suffix='.txt', text=True)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.path)
        os.remove(cls.invalid_path)

    def test_create(self):
        factory = XmlNodeFactory()

        node = factory.create(self.file_node)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, XmlBaseNode)
        node.close()
