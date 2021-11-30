from ..platform.cloudcms_object import CloudCMSObject
from collections import OrderedDict

class Project(CloudCMSObject):

    def __init__(self, client, data):
        super(Project, self).__init__(client, data)

    @classmethod
    def project_map(cls, client, data):
        return OrderedDict((project['_doc'], Project(client, project)) for project in data)