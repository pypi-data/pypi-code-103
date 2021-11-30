import time
from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.support import QName
from cloudcms.association import Directionality

class TestTraverse(AbstractWithRepositoryTest):
    
    @classmethod
    def setUpClass(cls):
        super(TestTraverse, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")

    def create_file(self, branch, parent, filename, is_folder):
        node = branch.create_node({'title': filename})
        node.add_feature('f:filename', {'filename': filename})
        if is_folder:
            node.add_feature('f:container', {})
        
        parent.associate(node, QName.create(qname='a:child'), directionality=Directionality.DIRECTED)

        return node

    def test_traverse(self):
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

        # test path resolves
        path = file5.resolve_path()
        self.assertEqual('/folder1/folder2/file5', path)

        paths = file5.resolve_paths()
        self.assertGreater(0, len(paths))

        traverse = {
            'depth': 1,
            'filter': 'ALL_BUT_START_NODE',
            'associations': {
                'a:child': 'ANY'
            }
        }
        time.sleep(5)

        results = rootNode.traverse(traverse)
        self.assertEqual(2, len(results.nodes))
        self.assertEqual(2, len(results.associations))