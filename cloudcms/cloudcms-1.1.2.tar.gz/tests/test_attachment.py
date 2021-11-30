from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.node import Node
from cloudcms.support import QName
from cloudcms.association import Directionality, Direction

class TestAttachment(AbstractWithRepositoryTest):
    
    @classmethod
    def setUpClass(cls):
        super(TestAttachment, cls).setUpClass()
        cls.branch = cls.repository.read_branch("master")
    
    def test_attachment(self):
        branch = type(self).branch
        node = branch.create_node()

        with open('./res/cloudcms.png', 'rb') as cloudcmsImage:
            node.upload_attachment(cloudcmsImage, 'image/png', attachment_id='default', filename='myImage')

        attachments = node.list_attachments()
        attachment = attachments['default']
        self.assertEqual('default', attachment.id)
        self.assertEqual('myImage', attachment.filename)
        self.assertEqual('image/png', attachment.content_type)
        self.assertTrue(attachment.length > 0)
        self.assertIsNotNone(attachment.object_id)
        
        dl = attachment.download_attachment()
        self.assertTrue(len(dl) > 0)
        dl_copy = node.download_attachment('default')
        self.assertEqual(dl, dl_copy)

        with open('./res/headphones.png', 'rb') as headphonesImage:
            node.upload_attachment(headphonesImage, 'image/png', attachment_id='another')

        attachments = node.list_attachments()
        self.assertEqual(2, len(attachments))

        node.delete_attachment('default')
        attachments = node.list_attachments()
        self.assertEqual(1, len(attachments))

        attachment = attachments['another']
        self.assertEqual('another', attachment.id)
        self.assertEqual('another', attachment.filename)
        self.assertEqual('image/png', attachment.content_type)
        self.assertTrue(attachment.length > 0)
        self.assertIsNotNone(attachment.object_id)
        