from collections import OrderedDict

class Attachment(object):

    def __init__(self, attachable, obj):
        self.attachable = attachable

        self.id = obj.get('attachmentId')
        self.object_id = obj.get('objectId')
        self.length = int(obj.get('length'))
        self.filename = obj.get('filename')
        self.content_type = obj.get('contentType')
    
    def download_attachment(self):
        return self.attachable.download_attachment(self.id)

    @classmethod
    def attachments_map(cls, attachable, data):
        return OrderedDict((attachment['attachmentId'], Attachment(attachable, attachment)) for attachment in data)
