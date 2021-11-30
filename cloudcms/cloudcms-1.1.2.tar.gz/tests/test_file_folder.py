from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.node import Node
from cloudcms.support import QName
from cloudcms.association import Directionality, Direction

class TestFileFolder(AbstractWithRepositoryTest):
    
    @classmethod
    def setUpClass(cls):
        super(TestFileFolder, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")

    def create_file(self, branch, parent, filename, is_folder):
        node = branch.create_node({'title': filename})
        node.add_feature('f:filename', {'filename': filename})
        if is_folder:
            node.add_feature('f:container', {})
        
        parent.associate(node, QName.create(qname='a:child'), directionality=Directionality.DIRECTED)

        return node

    def test_file_folder(self):
        # folder1
        # file1
        # folder1/folder2
        # folder1/file2
        # folder1/file4
        # folder1/folder2/file3
        # folder1/folder2/file5
        branch = type(self).branch
        rootNode = branch.root_node()

        folder1 = self.create_file(branch, rootNode, 'folder1', True)
        file1 = self.create_file(branch, rootNode, 'file1', False)
        folder2 = self.create_file(branch, folder1, 'folder2', True)
        file2 = self.create_file(branch, folder1, 'file2', False)
        file3 = self.create_file(branch, folder2, 'file3', False)
        file4 = self.create_file(branch, folder1, 'file4', False)
        file5 = self.create_file(branch, folder2, 'file5', False)

        tree = rootNode.file_folder_tree()
        self.assertEqual(2, len(tree['children']))

        child = tree['children'][0]
        self.assertIsNotNone(child['filename'])
        self.assertIsNotNone(child['label'])
        self.assertIsNotNone(child['path'])
        self.assertIsNotNone(child['typeQName'])
        self.assertIsNotNone(child['qname'])

        folder2Children = folder2.list_children()
        self.assertEqual(2, len(folder2Children))

        folder2Relatives = folder2.list_relatives(QName.create('a:child'), Direction.ANY)
        self.assertEqual(3, len(folder2Relatives))

        folder2RelativesQueried = folder2.query_relatives(QName.create('a:child'), Direction.ANY, {'title': 'file3'})
        self.assertEqual(1, len(folder2RelativesQueried))
