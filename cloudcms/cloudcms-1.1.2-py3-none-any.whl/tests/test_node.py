import time
from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.node import Node
from cloudcms.support import QName
from cloudcms.association import Directionality

class TestNode(AbstractWithRepositoryTest):
    
    @classmethod
    def setUpClass(cls):
        super(TestNode, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")

    def create_file(self, branch, parent, filename, is_folder):
        node = branch.create_node({'title': filename})
        node.add_feature('f:filename', {'filename': filename})
        if is_folder:
            node.add_feature('f:container', {})
        
        parent.associate(node, QName.create(qname='a:child'), directionality=Directionality.DIRECTED)

        return node


    def test_node_crud(self):
        branch = type(self).branch

        nodeObj = {
            "title": "MyNode"
        }
        node = branch.create_node(nodeObj)

        nodeRead = branch.read_node(node._doc)
        self.assertEqual(node.data, nodeRead.data)

        node.data["title"] = "New Title"
        node.update()

        nodeRead.reload()
        self.assertEqual(node.data["title"], nodeRead.data["title"])

        node.delete()
        nodeRead = branch.read_node(node._doc)
        self.assertIsNone(nodeRead)


    def test_node_query_search_find(self):
        branch = type(self).branch

        nodeObj1 = {
            "title": "Cheese burger",
            "meal": "lunch"
        }
        nodeObj2 = {
            "title": "Ham burger",
            "meal": "lunch"
        }
        nodeObj3 = {
            "title": "Turkey sandwich",
            "meal": "lunch"
        }
        nodeObj4 = {
            "title": "Oatmeal",
            "meal": "breakfast"
        }

        node1 = branch.create_node(nodeObj1)
        node2 = branch.create_node(nodeObj2)
        node3 = branch.create_node(nodeObj3)
        node4 = branch.create_node(nodeObj4)

        # Wait for nodes to index
        time.sleep(10)

        query = {
            "meal": "lunch"
        }
        queryNodes = branch.query_nodes(query)
        self.assertEqual(3, len(queryNodes))
        self.assertTrue(node1._doc in queryNodes.keys())
        self.assertTrue(node2._doc in queryNodes.keys())
        self.assertTrue(node3._doc in queryNodes.keys())

        find = {
            "search": "burger"
        }
        findNodes = branch.find_nodes(find)
        self.assertEqual(2, len(findNodes))
        self.assertTrue(node1._doc in findNodes.keys())
        self.assertTrue(node2._doc in findNodes.keys())

        searchNodes = branch.search_nodes('burger')
        self.assertEqual(2, len(searchNodes))
        self.assertTrue(node1._doc in searchNodes.keys())
        self.assertTrue(node2._doc in searchNodes.keys())

        node1.delete()
        node2.delete()
        node3.delete()
        node4.delete()

    def test_features(self):
        branch = type(self).branch
        node = branch.create_node({})
        featureIds = node.get_feature_ids()
        self.assertTrue(len(featureIds) > 0)

        node.add_feature('f:filename', {'filename': 'file1'})
        featureIds = node.get_feature_ids()
        self.assertTrue('f:filename' in featureIds)
        self.assertTrue(node.has_feature('f:filename'))
        featureObj = node.get_feature('f:filename')
        self.assertEqual('file1', featureObj.get('filename'))

        node.remove_feature('f:filename')
        featureIds = node.get_feature_ids()
        self.assertFalse('f:filename' in featureIds)
        self.assertFalse(node.has_feature('f:filename'))
        self.assertIsNone(node.get_feature('f:filename'))

        node.delete()

    def test_translations(self):
        branch = type(self).branch
        rootNode = branch.root_node()
        
        node = self.create_file(branch, rootNode, 'theNode', False)
        german = node.create_translation('de_DE', '1.0', {'title': 'german node'})
        self.assertIsNotNone(german)
        
        spanish1 = node.create_translation('es_ES', '1.0', {'title': 'spanish node'})
        spanish2 = node.create_translation('es_ES', '2.0', {'title': 'spanish node 2'})

        editions = node.get_translation_editions()
        self.assertEqual(2, len(editions))

        locales = node.get_translation_locales('1.0')
        self.assertEqual(2, len(locales))

        translation = node.read_translation('es_MX', edition='2.0')
        self.assertEqual('spanish node 2', translation.get_string('title'))

    def test_change_qname(self):
        branch = type(self).branch

        nodeObj = {
            '_type': 'n:node',
            'title': 'Test node'
        }

        node = branch.create_node(nodeObj)

        node.change_node_qname('o:blah')
        node.reload()

        self.assertEqual('o:blah', node.data['_qname'])
        

    def test_versions(self):
        branch = type(self).branch
        nodeObj = {
            'title': 'my node'
        }

        node = branch.create_node(nodeObj)
        firstChangeset = node.data['_system']['changeset']
        self.assertIsNotNone(firstChangeset)

        node.data['title'] = 'new stuff'
        node.update()
        node.reload()
        self.assertEqual('new stuff', node.data['title'])

        versions = node.list_versions()
        self.assertEqual(2, len(versions))

        firstVersion = node.read_version(firstChangeset)
        self.assertEqual('my node', firstVersion.data['title'])


        restoredVersion = node.restore_version(firstChangeset)
        self.assertEqual('my node', restoredVersion.data['title'])
