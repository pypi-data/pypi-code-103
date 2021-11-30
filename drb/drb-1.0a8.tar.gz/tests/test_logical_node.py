import pathlib
import unittest
import re
from typing import List
import operator
from functools import partial

from drb import DrbNode
from drb.predicat import Predicate
from drb.utils.logical_node import DrbLogicalNode
from drb.exceptions import DrbException, DrbNotImplementationException


class NameMatchPredicate(Predicate):
    def __init__(self, pattern: str):
        self._pattern = re.compile(pattern)

    def matches(self, node: DrbNode) -> bool:
        if self._pattern.match(node.name):
            return True
        return False


class NumericalAttributeMatchesPredicate(Predicate):
    def __init__(self, name: str, condition):
        self._name = name
        self.condition = condition

    def matches(self, node: DrbNode) -> bool:
        try:
            value = node.get_attribute(self._name)
            if self.condition(value):
                return True
        except DrbException:
            # name not found : return false
            pass
        return False


class TestLogicalNode(unittest.TestCase):
    def _test_node(self):
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        child_ = DrbLogicalNode(source="/path/to/data/child_")

        node = DrbLogicalNode(source="/path/to/data")
        node.insert_child(0, child1)
        node.insert_child(0, child2)
        node.insert_child(0, child3)

        # 4 occurrences of child
        node.insert_child(0, child_)
        node.insert_child(0, child_)
        node.insert_child(0, child_)
        node.insert_child(0, child_)

        return DrbLogicalNode(node)

    def test_init(self):
        node = DrbLogicalNode(source="/path/to/data")
        self.assertEqual(node.path.path, "/path/to/data")
        self.assertEqual(node.name, "data")
        node.close()

        node = DrbLogicalNode(source="http://www.gael.fr/path/to/data")
        self.assertEqual(node.path.path, "/path/to/data")
        self.assertEqual(node.name, "data")
        node.close()

        node = DrbLogicalNode(
            source="http://www.gael.fr/path/to/data.zip!/content/data")
        self.assertEqual(node.path.path, "/path/to/data.zip!/content/data")
        self.assertEqual(node.path.archive, "/path/to/data.zip")
        self.assertEqual(node.name, "data")
        node.close()

        node = DrbLogicalNode(source=pathlib.Path("/path/to/data"))
        self.assertEqual(node.path.name, "/path/to/data")
        self.assertEqual(node.name, "data")
        node.close()

        new_node = DrbLogicalNode(source=node)
        self.assertEqual(new_node.path.name, "/path/to/data")
        self.assertEqual(new_node.name, node.name)
        node.close()

    def test_attributes(self):
        attributes = {
            ('name1', 'namespace1'): 'value1',
            ('name2', 'namespace2'): 'value2',
            ('name3', 'namespace3'): 'value3',
            ('name4', 'namespace4'): 'value4',
        }
        w = DrbLogicalNode(source="/path/to/data")
        node = DrbLogicalNode(w)
        node.attributes = attributes

        self.assertEqual(node.attributes, attributes)

        self.assertEqual(node.get_attribute('name1', 'namespace1'), 'value1')
        self.assertEqual(node.get_attribute('name4', 'namespace4'), 'value4')
        with self.assertRaises(DrbException):
            node.get_attribute('name4', 'namespace5')

        pass

    def test_children_path(self):
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        child4 = DrbLogicalNode(source="/path/to/data/child4")

        node = DrbLogicalNode(source="/path/to/data")
        self.assertEqual(len(node), 0)

        with self.assertRaises(KeyError):
            self.assertEqual(node['child'], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[0], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[-1], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[2], None)
        with self.assertRaises(DrbException):
            self.assertEqual(node.remove_child(2), None)
        with self.assertRaises(DrbException):
            self.assertEqual(node.replace_child(2, child1), None)

        self.assertEqual(node.has_child(), False)

        # Shall not raise exception
        node.insert_child(5, child1)
        self.assertEqual(len(node), 1)
        node.insert_child(10, child2)
        self.assertEqual(len(node), 2)
        node.insert_child(0, child3)
        self.assertEqual(len(node), 3)

        node.replace_child(2, child4)
        self.assertEqual(len(node), 3)

        node.remove_child(0)
        self.assertEqual(len(node), 2)
        node.remove_child(0)
        node.remove_child(0)

        with self.assertRaises(DrbException):
            node.remove_child(0)

        node.children = [child1, child2, child3, child4]

        self.assertEqual(len(node), 4)
        self.assertEqual(node.has_child(), True)
        self.assertEqual(node["child1", 1], child1)
        self.assertEqual(node["child2", 1], child2)
        self.assertEqual(node["child3", 1], child3)
        self.assertEqual(node["child4", 1], child4)
        self.assertEqual(node['child1'][0], child1)

        self.assertEqual(node[0], child1)
        self.assertEqual(node[3], child4)
        self.assertEqual(node[-1], child4)

        with self.assertRaises(KeyError):
            self.assertEqual(node['child1', 0], None)
        with self.assertRaises(KeyError):
            self.assertEqual(node['childen123', 1], None)
        with self.assertRaises(KeyError):
            self.assertEqual(node['childen123'], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[15], None)

    def test_children_node(self):
        wrapped = DrbLogicalNode(source="/path/to/data/node")
        child1 = DrbLogicalNode(source="/path/to/data/node/child1")
        child2 = DrbLogicalNode(source="/path/to/data/node/child2")

        node = DrbLogicalNode(source=wrapped)

        self.assertEqual(len(node), 0)

        with self.assertRaises(DrbException):
            self.assertEqual(node/'child1', None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[0], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[-1], None)
        with self.assertRaises(IndexError):
            self.assertEqual(node[2], None)
        with self.assertRaises(DrbException):
            self.assertEqual(node.remove_child(2), None)
        with self.assertRaises(DrbException):
            self.assertEqual(node.replace_child(2, child1), None)

        self.assertEqual(node.has_child(), False)

        self.assertEqual(node.name, "node")
        self.assertEqual(node.namespace_uri, None)
        self.assertEqual(node.value, None)

        # Shall not raise exception
        node.insert_child(5, child1)
        self.assertEqual(len(node), 1)

        node.replace_child(0, child1)
        self.assertEqual(len(node), 1)

        node.remove_child(0)
        self.assertEqual(len(node), 0)
        with self.assertRaises(DrbException):
            node.remove_child(0)

        children = [child1, child2]
        node.children = children

        self.assertEqual(node.children, children)

        self.assertEqual(len(node), 2)
        self.assertEqual(node.has_child(), True)
        self.assertEqual(node["child1", 1], child1)
        self.assertEqual(node["child2", 1], child2)
        with self.assertRaises(KeyError):
            self.assertEqual(node["child2", 10], None)

        self.assertEqual((node / "child1")[0], child1)

        self.assertEqual(node[0], child1)
        self.assertEqual(node[-1], child2)
        self.assertEqual(node[1], child2)

        with self.assertRaises(IndexError):
            self.assertEqual(node[3], child2)

        self.assertEqual(node[0], child1)
        self.assertEqual(node[-1], child2)

        with self.assertRaises(KeyError):
            self.assertEqual(node['child1', 0], None)
        with self.assertRaises(KeyError):
            self.assertEqual(node['childen123', 1], None)
        with self.assertRaises(KeyError):
            self.assertEqual(node['childen123'], None)
        with self.assertRaises(DrbException):
            self.assertEqual(node/'childen123', None)

    def test_str_repr(self):
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        node = DrbLogicalNode(source="/path/to/data")

        node.insert_child(5, child1)
        node.insert_child(10, child2)
        node.insert_child(0, child3)

        self.assertEqual(str(node.children),
                         '[<child3/>, <child1/>, <child2/>]')

        attributes = {
            ('name1', 'nsa'): 'value1',
            ('name2', 'nsa'): 'value2',
        }

        child1.attributes = attributes
        child1.namespace_uri = "ns"
        child2.value = "value"
        self.assertEqual(str(node.children),
                         '[<child3/>, <ns:child1 "nsa:name1"="value1" '
                         '"nsa:name2"="value2"/>, <child2>value</child2>]')

    def test_parent(self):
        parent = DrbLogicalNode(source="/path/to/data")
        child = DrbLogicalNode(source="/path/to/data/node/child")
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)

        node.parent = parent
        self.assertEqual(node.parent, parent)
        parent.append_child(node)
        node.append_child(child)

        self.assertEqual(parent['node', None, 1], node)
        self.assertEqual(node.parent, parent)

    def test_name(self):
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)
        self.assertEqual(node.name, 'node')
        node.name = "new_name"
        self.assertEqual(node.name, 'new_name')

    def test_namespace(self):
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)
        self.assertEqual(node.namespace_uri, None)
        node.namespace_uri = 'http://www.gael.fr#'
        self.assertEqual(node.namespace_uri, 'http://www.gael.fr#')

    def test_value(self):
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)
        self.assertEqual(node.value, None)
        node.value = "value"
        self.assertEqual(node.value, 'value')

    def test_close(self):
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)
        node.close()

    def test_impl(self):
        w = DrbLogicalNode(source="/path/to/data/node")
        node = DrbLogicalNode(w)
        self.assertEqual(node.has_impl(str), False)
        with self.assertRaises(DrbException):
            self.assertEqual(node.get_impl(str), None)

    def test_append_child_son(self):
        class SonDrbLogicalNode(DrbLogicalNode):
            def __init__(self, path, parent: DrbNode = None):
                DrbLogicalNode.__init__(self, source=path)
                self._parent: DrbNode = parent

            @property
            def children(self) -> List[DrbNode]:
                if self._children is None:
                    self._children = []
                return self._children

        node = SonDrbLogicalNode("/path/to/data/node")
        node_child = DrbLogicalNode(source="/path/to/data/node.child")

        node.append_child(node_child)
        self.assertEqual(len(node), 1)

    def test_insert_child_son(self):
        class SonDrbLogicalNode(DrbLogicalNode):
            def __init__(self, path, parent: DrbNode = None):
                DrbLogicalNode.__init__(self, source=path)
                self._parent: DrbNode = parent

            @property
            def children(self) -> List[DrbNode]:
                if self._children is None:
                    self._children = []
                return self._children

        node = SonDrbLogicalNode("/path/to/data/node")
        node_child = DrbLogicalNode(source="/path/to/data/node.child")

        node.insert_child(0, node_child)
        self.assertEqual(len(node), 1)

    def test_slash(self):
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        child4 = DrbLogicalNode(source="/path/to/data/child_bad")
        node = DrbLogicalNode(source="/path/to/data")
        node.insert_child(5, child1)
        node.insert_child(10, child2)
        node.insert_child(0, child3)
        node.insert_child(0, child4)
        # Check type str
        self.assertEqual(child1, (node/'child1')[0])
        self.assertEqual(child2, (node/'child2')[0])
        self.assertEqual(1, len(node / 'child3'))

        # checks nodes
        self.assertEqual(child1, (node / child1)[0])
        self.assertEqual(child2, (node / child2)[0])
        self.assertEqual(1, len(node / child3))

        # Check predicates
        predicate = NameMatchPredicate(r'child\d')
        self.assertEqual(3, len(node / predicate))

        predicate = NameMatchPredicate(r'child')
        self.assertEqual(4, len(node / predicate))

        predicate = NameMatchPredicate(r'child_')
        self.assertEqual(1, len(node / predicate))

        with self.assertRaises(DrbNotImplementationException):
            from drb.path import parse_path
            path = parse_path('child1')
            self.assertEqual(child1, node/path)

    def test_brace_python(self):
        # This dictionary simulates a hierarchy of drb nodes.
        # This test case is used to compare DrbNode behavior with dictionary
        # braces behavior.
        dictionary = dict(
            {
                ('name1', 'ns1'):
                    {
                        ('child_name1', 'child_ns1'):
                            {
                                ('child_child_name1', 'child_child_ns1'):
                                    {
                                        ('child_child_child_name1',
                                         'child_child_child_ns1'): "Value1"
                                    }
                            }
                    },
                ('name2', 'ns2'):
                    {
                        ('child_name2', 'child_ns2'):
                            {
                                ('child_child_name2', 'child_child_ns2'):
                                    {
                                        ('child_child_child_name2',
                                         'child_child_child_ns2'): "Value2"
                                    }
                            }
                    },
                ('name2', 'ns2'):
                    {
                        ('child_name2', 'child_ns2'):
                            {
                                ('child_child_name2', 'child_child_ns2'):
                                    {
                                        ('child_child_child_name2',
                                         'child_child_child_ns2'): "Value2.1"
                                    }
                            }
                    },
                ('name3', 'ns3'):
                    {
                        ('child_name3', 'child_ns3'):
                            {
                                ('child_child_name3', 'child_child_ns3'):
                                    {
                                        ('child_child_child_name3',
                                         'child_child_child_ns3'): "Value3"
                                    }
                            }
                    }
            })
        self.assertEqual('Value1', dictionary['name1', 'ns1']
                         ['child_name1', 'child_ns1']
                         ['child_child_name1', 'child_child_ns1']
                         ['child_child_child_name1', 'child_child_child_ns1'])

        # In this case the 1st "child_name2" is overwitten by 2nd one.
        # This means dictionary in python are maps of item where occurrence is
        # not supported.
        # Then, the notation dict['name'][1] that should mean
        #    2nd occurrence of 'name' key is not supported by dict
        #    implementation.
        self.assertEqual('Value2.1', dictionary['name2', 'ns2']
                         ['child_name2', 'child_ns2']
                         ['child_child_name2', 'child_child_ns2']
                         ['child_child_child_name2', 'child_child_child_ns2'])

    def test_brace_node(self):
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        child_ = DrbLogicalNode(source="/path/to/data/child_")
        child_with_ns = DrbLogicalNode(source="/path/to/data/child_with_ns")
        child_with_ns.namespace_uri = 'ns'

        node = DrbLogicalNode(source="/path/to/data")
        node.insert_child(0, child1)
        node.insert_child(0, child2)
        node.insert_child(0, child3)

        # 4 occurrences of child
        node.insert_child(0, child_)
        node.insert_child(0, child_)
        node.insert_child(0, child_)
        node.insert_child(0, child_)
        node.insert_child(50, child_with_ns)
        # Check type str
        self.assertEqual(child1, node['child1'][0])
        self.assertEqual(child2, node['child2'][0])
        self.assertEqual(1, len(node['child3']))
        self.assertEqual(4, len(node['child_']))
        self.assertEqual(child_, node['child_'][3])

        # Check type int case = index among children
        self.assertEqual(child2, node[5])

        # Check type tuple case = (name, namespace, occurrence)
        self.assertEqual(child_, node['child_', 4])
        self.assertEqual(child1, node['child1', 1])
        self.assertEqual(child1, node[('child1', )][0])
        self.assertEqual(child_with_ns, node['child_with_ns', 'ns'][0])
        self.assertEqual(child_with_ns, node['child_with_ns', 'ns', 1])
        with self.assertRaises(KeyError):
            self.assertEqual(child_with_ns, node['child_with_ns', child_])
        with self.assertRaises(KeyError):
            self.assertEqual(child_with_ns,
                             node['child_with_ns', 'ns', 'toto'])
        with self.assertRaises(KeyError):
            self.assertEqual(child_with_ns,
                             node['child_with_ns', 'ns', 'toto', 1])
        with self.assertRaises(KeyError):
            self.assertEqual(child_with_ns, node['child_with_ns', 'ns', 0])
        with self.assertRaises(KeyError):
            self.assertEqual(None, node['child1', 2])
        with self.assertRaises(TypeError):
            self.assertEqual(None, node[pathlib.Path('/path')])

        # Check type DrbNode
        self.assertEqual(child1, node[child1][0])
        self.assertEqual(child_, node[child_][0])
        self.assertEqual(4, len(node[child_]))

        # Check predicates
        predicate = NameMatchPredicate(r'child\d')
        self.assertEqual(3, len(node[predicate]))

        predicate = NameMatchPredicate(r'child')
        self.assertEqual(8, len(node[predicate]))

        predicate = NameMatchPredicate(r'child_')
        self.assertEqual(5, len(node[predicate]))

        with self.assertRaises(TypeError):
            from drb.path import parse_path
            path = parse_path('child1')
            self.assertEqual(child_, node[path])

    def test_len_node(self):
        self.assertEqual(7, len(self._test_node()))

    def test_predicate_among_numerical_attributes(self):
        attributes = {
            ('name1', None): 1,
            ('name2', None): 2,
            ('name3', None): 3,
            ('name4', None): 4,
        }

        node = DrbLogicalNode(source="/path/to/data")
        child1 = DrbLogicalNode(source="/path/to/data/child1")
        child2 = DrbLogicalNode(source="/path/to/data/child2")
        child3 = DrbLogicalNode(source="/path/to/data/child3")
        child4 = DrbLogicalNode(source="/path/to/data/child4")

        child1.attributes = attributes
        child2.attributes = attributes
        child3.attributes = attributes
        child4.attributes = attributes

        node.insert_child(0, child1)
        node.insert_child(0, child2)
        node.insert_child(0, child3)
        node.insert_child(0, child4)

        condition = partial(operator.ge, 3)
        predicate = NumericalAttributeMatchesPredicate('name3', condition)
        self.assertEqual(4, len(node[predicate]))

        condition = partial(operator.gt, 3)
        predicate = NumericalAttributeMatchesPredicate('name3', condition)
        self.assertEqual(0, len(node[predicate]))

        node['child3'][0].attributes = None
        condition = partial(operator.ge, 3)
        predicate = NumericalAttributeMatchesPredicate('name3', condition)
        self.assertEqual(3, len(node[predicate]))

    def test_add_attribute(self):
        attributes = {
            ('name1', 'namespace1'): 'value1',
            ('name2', 'namespace2'): 'value2',
            ('name3', 'namespace3'): 'value3',
            ('name4', 'namespace4'): 'value4',
        }
        w = DrbLogicalNode(source="/path/to/data")
        node = DrbLogicalNode(w)
        node.attributes = attributes

        node.add_attribute('name5', 'value5', 'namespace5')
        node.add_attribute('name5', 'value5_no_namespace')

        self.assertEqual(node.get_attribute('name5'), 'value5_no_namespace')
        self.assertEqual(node.get_attribute('name5', 'namespace5'), 'value5')

        with self.assertRaises(DrbException):
            node.add_attribute('name5', 'duplicate', 'namespace5')

    def test_remove_attribute(self):
        attributes = {
            ('name1', 'namespace1'): 'value1',
            ('name2', 'namespace2'): 'value2',
            ('name3', 'namespace3'): 'value3',
            ('name4', 'namespace4'): 'value4',
        }
        w = DrbLogicalNode(source="/path/to/data")
        node = DrbLogicalNode(w)
        node.attributes = attributes

        self.assertEqual(node.get_attribute('name3', 'namespace3'), 'value3')

        node.remove_attribute('name3', 'namespace3')

        self.assertEqual(len(node.attributes), 3)

        with self.assertRaises(DrbException):
            node.get_attribute('name3', 'namespace3')

        with self.assertRaises(DrbException):
            node.remove_attribute('name3', 'namespace_fake')

    def test_parent_in_kwargs(self):
        parent = DrbLogicalNode(source="/path/to/data")
        child = DrbLogicalNode(source="/path/to/data/node/child")
        self.assertEqual(child.parent, None)
        child = DrbLogicalNode(source="/path/to/data/node/child",
                               parent=parent)
        self.assertEqual(child.parent, parent)
