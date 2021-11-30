import unittest
from drb.node import DrbNode
from drb.factory.factory import DrbFactory
from .utils import DrbTestNode


class DefaultFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return DrbTestNode(f"DefaultNode_{node.name}")


class TestDrbFactory(unittest.TestCase):
    def test_drb_factory_check_uri(self):
        uris = [
            ("file://my/path/to/my_file/", "DefaultNode_"),
            ("/my/path/to/my_file/", "DefaultNode_"),
            ("file://my/path/to/my_file", "DefaultNode_my_file"),
            ("/my/path/to/my_file", "DefaultNode_my_file"),
            ("http://avp.wikia.com/wiki/ht_file", "DefaultNode_ht_file"),
            ("AAA", "DefaultNode_AAA"),
            ("ftp://ftp.fe.fr/ms/fp.cs.org/7.2.15/ft_file",
             "DefaultNode_ft_file")]

        factory = DefaultFactory()
        for uri, expected_name in uris:
            self.assertEqual(factory.create(uri).name, expected_name,
                             f'Uri not supported: {uri}')
