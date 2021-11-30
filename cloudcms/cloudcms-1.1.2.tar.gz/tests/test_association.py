from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.support import QName
from cloudcms.association import Directionality, Direction


class TestAssociation(AbstractWithRepositoryTest):

    @classmethod
    def setUpClass(cls):
        super(TestAssociation, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")
    

    def test_associate_unassociate(self):
        branch = type(self).branch

        node1 = branch.create_node({'title': 'node1'})
        node2 = branch.create_node({'title': 'node2'})
        node3 = branch.create_node({'title': 'node3'})

        # Associate node 1 directed to node 2 with a:child
        association1 = node1.associate(node2, QName.create('a:child'))
        self.assertEqual(Directionality.DIRECTED, association1.get_directionality())
        self.assertEqual(node1.get_id(), association1.get_source_node_id())
        self.assertEqual(node2.get_id(), association1.get_target_node_id())

        source = association1.read_source_node()
        self.assertEqual(node1.get_id(), source.get_id())
        target = association1.read_target_node()
        self.assertEqual(node2.get_id(), target.get_id())

        # Associate node 1 undirected to node 3 with a:linked
        association2 = node1.associate(node3, QName.create('a:linked'), directionality=Directionality.UNDIRECTED, data={'test': 'field'})
        self.assertEqual(Directionality.UNDIRECTED, association2.get_directionality())
        self.assertEqual(node1.get_id(), association2.get_source_node_id())
        self.assertEqual(node3.get_id(), association2.get_target_node_id())

        allAssociations = node1.associations()
        self.assertEqual(3, len(allAssociations))

        outgoingAssociations = node1.associations(direction=Direction.OUTGOING)
        self.assertEqual(2, len(outgoingAssociations))

        incomingAssociations = node1.associations(direction=Direction.INCOMING)
        self.assertEqual(2, len(incomingAssociations))

        childAssociations = node1.associations(association_type_qname=QName.create(qname='a:child'))
        self.assertEqual(1, len(childAssociations))

        node1.unassociate(node2, QName.create(qname='a:child'))
        node1.unassociate(node3, QName.create(qname='a:linked'), directionality=Directionality.UNDIRECTED)

        allAssociations = node1.associations()
        self.assertEqual(1, len(allAssociations))

    def test_child_of(self):
        branch = type(self).branch

        node1 = branch.create_node({'title': 'node1'})
        node2 = branch.create_node({'title': 'node2'})

        association = node1.child_of(node2)
        self.assertIsNotNone(association)
        self.assertEqual(Directionality.DIRECTED, association.get_directionality())

        source = association.read_source_node()
        self.assertEqual(node2.get_id(), source.get_id())
        target = association.read_target_node()
        self.assertEqual(node1.get_id(), target.get_id())

