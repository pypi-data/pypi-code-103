from ..platform import CloudCMSObject
from collections import OrderedDict

class Job(CloudCMSObject):

    def __init__(self, client, data):
        super(Job, self).__init__(client, data)
    
    @classmethod
    def job_map(cls, client, data):
        return OrderedDict((job['_doc'], Job(client, job)) for job in data)