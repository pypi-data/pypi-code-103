import os.path
import sys
import unittest
from uuid import UUID

from drb.utils.logical_node import DrbLogicalNode
from drb.utils.url_node import UrlNode
from drb.factory import DrbFactoryResolver
from drb.exceptions import DrbFactoryException


class TestDrbFactoryResolver(unittest.TestCase):
    mock_package_path: str = None
    resolver: DrbFactoryResolver = None
    signature_uuid: dict = None

    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)
        cls.mock_package_path = os.path.abspath(
            os.path.join(path, 'resources', 'packages'))
        sys.path.append(cls.mock_package_path)
        cls.resolver = DrbFactoryResolver()
        cls.signature_uuid = {
            'file': UUID('99e6ce18-276f-11ec-9621-0242ac130002'),
            'foobar': UUID('75eddcbc-2752-11ec-9621-0242ac130002'),
            'mem': UUID('09d14890-283b-11ec-9621-0242ac130002'),
            'zip': UUID('53794b50-2778-11ec-9621-0242ac130002'),
            'safe': UUID('c44c2f36-2779-11ec-9621-0242ac130002'),
            'sentinel-1': UUID('84a54dea-2800-11ec-9621-0242ac130002'),
            'sentinel-1-level0': UUID('4d28758a-2806-11ec-9621-0242ac130002'),
            'xml': UUID('aced0812-2830-11ec-9621-0242ac130002'),
            'txt': UUID('3d797648-281a-11ec-9621-0242ac130002'),
        }

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(cls.mock_package_path)

    def test_resolve_foobar(self):
        node = DrbLogicalNode('foobar:my-data')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['foobar'], signature.uuid)

    def test_resolve_mem(self):
        node = DrbLogicalNode('mem:my-data')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['mem'], signature.uuid)

    def test_resolve_file(self):
        node = DrbLogicalNode('file:///path/to/my-file.dat')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['file'], signature.uuid)

        node = DrbLogicalNode('/absolute/path/to/my-file.dat')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['file'], signature.uuid)

        node = DrbLogicalNode('relative/path/to/my-file.dat')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['file'], signature.uuid)

    def test_resolve_txt(self):
        source = 'text.txt'
        signature, base_node = self.resolver.resolve(source)
        self.assertEqual(self.signature_uuid['txt'], signature.uuid)
        self.assertIsInstance(base_node, UrlNode)

        source = DrbLogicalNode('text.txt')
        signature, base_node = self.resolver.resolve(source)
        self.assertEqual(self.signature_uuid['txt'], signature.uuid)
        self.assertIsInstance(base_node, DrbLogicalNode)

    def test_resolve_xml(self):
        node = DrbLogicalNode('content.xml')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['xml'], signature.uuid)
        self.assertIsInstance(base_node, DrbLogicalNode)

    def test_resolve_safe_product(self):
        node = DrbLogicalNode('TEST.SAFE')
        node.append_child(DrbLogicalNode('manifest.safe'))
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['safe'], signature.uuid)

        node = DrbLogicalNode('TEST.SAFE')
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['file'], signature.uuid)

    def test_resolve_sentinel_product(self):
        name = 'S1A_IW_SLC__1SDV_20211008T045534_20211008T045601_040023' \
               '_04BCCC_58BF.SAFE'
        node = DrbLogicalNode(name)
        node.append_child(DrbLogicalNode('manifest.safe'))
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['sentinel-1'], signature.uuid)

        name = 'S1A_IW_RAW__0SDV_20211008T045532_20211008T045604_040023' \
               '_04BCCC_56E7.SAFE'
        node = DrbLogicalNode(name)
        node.append_child(DrbLogicalNode('manifest.safe'))
        signature, base_node = self.resolver.resolve(node)
        self.assertEqual(self.signature_uuid['sentinel-1-level0'],
                         signature.uuid)

    def test_cannot_resolve(self):
        node = DrbLogicalNode('foo:my-data')
        with self.assertRaises(DrbFactoryException):
            self.resolver.resolve(node)

    def test_create(self):
        uri = UrlNode('foobar:///path/to/my-data')
        node = self.resolver.create(uri)
        self.assertEqual("Foobar_my-data", node.name)

        uri = UrlNode('mem:/my/path/to/my_file')
        node = self.resolver.create(uri)
        self.assertEqual("Mem_my_file", node.name)

    def test_url_resolution(self):
        url = 'mockurl://path/to/resource.rs/sub/path/foobar.data'
        node = self.resolver.create(url)
        self.assertIsNotNone(node)
        self.assertEqual("<class 'mock_data.MockDataNode'>", str(type(node)))
        self.assertEqual('foobar', node.name)

        url = 'fake://path/to/resource.rs/sub/path/foobar.fake'
        with self.assertRaises(DrbFactoryException):
            self.resolver.create(url)
