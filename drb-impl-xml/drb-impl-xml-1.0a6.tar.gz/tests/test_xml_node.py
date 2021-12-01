import io
import posixpath
import unittest
import os
import tempfile
from xml.etree.ElementTree import fromstring

from drb.exceptions import DrbNotImplementationException, DrbException
from drb_impl_file import DrbFileNode, DrbFileAttributeNames
from typing import Tuple

from drb_impl_xml import XmlNode, XmlBaseNode


class TestXmlNode(unittest.TestCase):
    def test_name(self):
        xml = '<foo></foo>'
        node = XmlNode(fromstring(xml))
        self.assertEqual('foo', node.name)
        xml = '<fb:foobar xmlns:fb="http://foobar.org/foobar"/>'
        node = XmlNode(fromstring(xml))
        self.assertEqual('foobar', node.name)

    def test_value(self):
        xml = '''<foo>hello world</foo>'''
        node = XmlNode(fromstring(xml))
        self.assertEqual('hello world', node.value)
        xml = '''<foo></foo>'''
        node = XmlNode(fromstring(xml))
        self.assertIsNone(node.value)
        xml = '''<foo><bar>foobar</bar></foo>'''
        node = XmlNode(fromstring(xml))
        self.assertIsNone(node.value)
        xml = '''<foo/>'''
        node = XmlNode(fromstring(xml))
        self.assertIsNone(node.value)

    def test_namespace_uri(self):
        xml = '<foobar>text</foobar>'
        node = XmlNode(fromstring(xml))
        self.assertIsNone(node.namespace_uri)

        namespace = 'https://gael-systems.com'
        xml = f'<g:drb xmlns:g="{namespace}">Data Request Broker</g:drb>'
        node = XmlNode(fromstring(xml))
        self.assertEqual(namespace, node.namespace_uri)

    def test_attributes(self):
        namespace = 'http://foobar.org/foo'
        xml = f'''<foo xmlns:f="{namespace}"
                       attr1="3" f:attr2="hello" attr3="false" />'''
        node = XmlNode(fromstring(xml))
        attributes = node.attributes
        self.assertIsNotNone(attributes)
        self.assertEqual(3, len(attributes))

        self.assertEqual('3', attributes[('attr1', None)])
        self.assertEqual('hello', attributes[('attr2', namespace)])
        self.assertEqual('false', attributes[('attr3', None)])

        xml = '''<foo />'''
        node = XmlNode(fromstring(xml))
        attributes = node.attributes
        self.assertIsNotNone(attributes)
        self.assertEqual(0, len(attributes))

    def test_parent(self):
        xml = '''<foo><bar>foobar</bar></foo>'''
        pn = XmlNode(fromstring(xml))
        child = pn[0]
        self.assertEqual(pn, child.parent)
        self.assertIsNone(pn.parent)

    def test_children(self):
        ns_foo = 'http://foobar.org/foo'
        xml = f'''
        <f:foobar xmlns:f="{ns_foo}">
            <f:foo>foobar_1</f:foo>
            <f:foo>foobar_2</f:foo>
            <f:foo>foobar_3</f:foo>
            <bar>foobar_4</bar>
            <bar>foobar_5</bar>
        </f:foobar>
        '''
        node = XmlNode(fromstring(xml))
        self.assertEqual(5, len(node.children))
        self.assertEqual('foo', node.children[2].name)
        self.assertEqual(ns_foo, node.children[2].namespace_uri)
        self.assertEqual('foobar_3', node.children[2].value)

        self.assertEqual('bar', node.children[4].name)
        self.assertIsNone(node.children[4].namespace_uri)
        self.assertEqual('foobar_5', node.children[4].value)

    def test_get_attribute(self):
        ns_foo = 'http://foobar.org/foo'
        ns_bar = 'http://foobar.org/bar'
        xml = f'''
        <foobar xmlns:b="{ns_bar}" xmlns:f="{ns_foo}">
            <foo b:attr1="3" f:attr2="hello" attr3="false"/>
        </foobar>'''
        node = XmlNode(fromstring(xml)[0])
        self.assertEqual('3', node.get_attribute('attr1', ns_bar))
        self.assertEqual('hello', node.get_attribute('attr2', ns_foo))
        self.assertEqual('false', node.get_attribute('attr3'))

        with self.assertRaises(DrbException):
            node.get_attribute('attr3', ns_foo)

    def test_has_child(self):
        xml = '''<foo><bar/></foo>'''
        node = XmlNode(fromstring(xml))
        self.assertTrue(node.has_child())
        xml = '''<bar>foobar</bar>'''
        node = XmlNode(fromstring(xml))
        self.assertFalse(node.has_child())
        xml = '''<bar/>'''
        node = XmlNode(fromstring(xml))
        self.assertFalse(node.has_child())

    def test_get_first_child(self):
        xml = '<foobar><foo/><bar/></foobar>'
        node = XmlNode(fromstring(xml))
        self.assertEqual('foo', node[0].name)

        xml = '<foobar><foo/></foobar>'
        node = XmlNode(fromstring(xml))
        self.assertEqual('foo', node[0].name)

        xml = '<foobar></foobar>'
        node = XmlNode(fromstring(xml))
        with self.assertRaises(IndexError):
            node[0]

        xml = '<foobar/>'
        node = XmlNode(fromstring(xml))
        with self.assertRaises(IndexError):
            node[0]

    def test_get_named_child(self):
        ns_foo = 'http://foobar.org/foo'
        ns_bar = 'http://foobar.org/bar'
        xml = f'''
        <f:foobar xmlns:f="{ns_foo}" xmlns:b="{ns_bar}">
            <f:foo>foobar_1</f:foo>
            <b:foo>foobar_2</b:foo>
            <f:foo>foobar_3</f:foo>
            <bar>foobar_4</bar>
            <bar>foobar_5</bar>
        </f:foobar>
        '''
        node = XmlNode(fromstring(xml))
        child = node[('foo', ns_foo)]
        self.assertIsInstance(child, list)
        self.assertEqual(2, len(child))

        child = node[('foo', ns_foo, 2)]
        self.assertIsInstance(child, XmlNode)
        self.assertEqual('foo', child.name)
        self.assertEqual(ns_foo, child.namespace_uri)
        self.assertEqual('foobar_3', child.value)

        with self.assertRaises(KeyError):
            node['fake']
        with self.assertRaises(KeyError):
            node[('foo', ns_foo, -1)]
        with self.assertRaises(KeyError):
            node[('foo', ns_foo, 42)]

    def test_get_child_at(self):
        xml = f'''
        <foobar>
            <foo>foobar_1</foo>
            <foo>foobar_2</foo>
            <foo>foobar_3</foo>
            <bar>foobar_4</bar>
            <bar>foobar_5</bar>
        </foobar>
        '''
        node = XmlNode(fromstring(xml))
        self.assertEqual('foobar_1', node[0].value)
        self.assertEqual('foobar_2', node[1].value)
        self.assertEqual('foobar_3', node[2].value)
        self.assertEqual('foobar_4', node[3].value)
        self.assertEqual('foobar_5', node[4].value)

        with self.assertRaises(IndexError):
            node[2]

            node[-43]

    def test_get_children_number(self):
        xml = '<foobar><foo/><foo/><foo/><bar/><bar/></foobar>'
        node = XmlNode(fromstring(xml))
        self.assertEqual(5, len(node))

        xml = '<foobar>example</foobar>'
        node = XmlNode(fromstring(xml))
        self.assertEqual(0, len(node))

        xml = '<foobar />'
        node = XmlNode(fromstring(xml))
        self.assertEqual(0, len(node))

    def test_has_impl(self):
        node = XmlNode(fromstring('<a>ok</a>'))
        self.assertTrue(node.has_impl(str))
        node = XmlNode(fromstring('<a><b>ok</b></a>'))
        self.assertFalse(node.has_impl(str))

    def test_get_impl(self):
        node = XmlNode(fromstring('<a>ok</a>'))
        self.assertEqual('ok', node.get_impl(str))
        node = XmlNode(fromstring('<a><b>ok</b></a>'))
        with self.assertRaises(DrbNotImplementationException):
            node.get_impl(str)
        with self.assertRaises(DrbNotImplementationException):
            node.get_impl(list)

    def test_close(self):
        # Nothing shall happen
        XmlNode(fromstring('<a>ok</a>')).close()

    def test_path(self):
        node = XmlNode(fromstring('<a><b>hello</b></a>'))
        self.assertEqual('/a', node.path.path)
        self.assertEqual('/a/b', node[0].path.path)


class TestXmlBaseNode(unittest.TestCase):
    xml = """<fb:foobar xmlns:fb="https://foobar.org/foobar"
                        fb:foo="hello"
                        fb:bar="world" />"""
    path = None
    file_node = None
    node = None

    @classmethod
    def create_tmp_node(cls) -> Tuple[XmlBaseNode, DrbFileNode, str]:
        fd, path = tempfile.mkstemp(suffix='.xml', text=True)
        with os.fdopen(fd, 'w') as file:
            file.write(cls.xml)
            file.flush()

        file_node = DrbFileNode(path)
        with io.FileIO(path) as stream:
            return XmlBaseNode(file_node, stream), file_node, path

    @classmethod
    def setUpClass(cls) -> None:
        cls.node, cls.file_node, cls.path = cls.create_tmp_node()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.path)
        cls.node.close()

    def test_name(self):
        self.assertEqual(self.file_node.name, self.node.name)

    def test_value(self):
        self.assertEqual(self.file_node.value, self.node.value)

    def test_namespace_uri(self):
        self.assertEqual(self.file_node.namespace_uri, self.node.namespace_uri)

    def test_attributes(self):
        self.assertEqual(self.file_node.attributes, self.node.attributes)

    def test_parent(self):
        self.assertEqual(self.file_node.parent, self.node.parent)

    def test_children(self):
        children = self.node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(1, len(children))
        self.assertIsInstance(children[0], XmlNode)

    def test_get_attribute(self):
        name, ns = (DrbFileAttributeNames.DIRECTORY.value, None)
        self.assertEqual(self.file_node.get_attribute(name, ns),
                         self.node.get_attribute(name, ns))

    def test_has_child(self):
        self.assertTrue(self.node.has_child())

    def test_get_named_child(self):
        name, ns = 'foobar', 'https://foobar.org/foobar'
        self.assertEqual(self.node.children[0], self.node[(name, ns)][0])
        self.assertEqual(self.node.children[0], self.node[(name, ns, 1)])
        with self.assertRaises(KeyError):
            self.node[(name, ns, 3)]
        with self.assertRaises(KeyError):
            self.node[(name, ns, 'fake')]
        with self.assertRaises(KeyError):
            self.node[(name, 1)]
        with self.assertRaises(KeyError):
            self.node[(name, ns, -1)]

    def test_get_children_number(self):
        self.assertEqual(1, len(self.node))

    def test_close(self):
        node, file_node, path = self.create_tmp_node()
        # Shall not raise exception, XmlBaseNode shall close base node IO
        # implementation and itself.
        node.close()
        file_node.close()

    def test_path(self):
        children = self.node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(1, len(children))
        self.assertIsInstance(children[0], XmlNode)

        self.assertEqual(children[0].path.path, self.node.path.path
                         + posixpath.sep + self.node[0].name)
