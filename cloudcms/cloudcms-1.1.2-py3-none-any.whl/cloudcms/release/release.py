from ..repository.repository_object import RepositoryObject
from collections import OrderedDict

class Release(RepositoryObject):

    def __init__(self, repository, data):
        super(Release, self).__init__(repository, data)

    @classmethod
    def release_map(cls, repository, data):
        return OrderedDict((release['_doc'], Release(repository, release)) for release in data)