from collections import OrderedDict

from cloudcms.release import release
from ..platform import CloudCMSObject
from ..branch import Branch
from ..release import Release
from ..error import RequestError


class Repository(CloudCMSObject):

    def __init__(self, client, data):
        super(Repository, self).__init__(client, data)

        self.platform_id = data['platformId']

    def uri(self):
        return '/repositories/' + self._doc

    # Branches

    def list_branches(self):
        uri = self.uri() + '/branches/'
        res = self.client.get(uri)
        return Branch.branch_map(self, res['rows'])

    def query_branches(self, query, pagination={}):
        uri = self.uri() + '/branches/query'
        response = self.client.post(uri, pagination, query)
        return Branch.branch_map(self, response['rows'])

    def read_branch(self, branch_id):
        uri = self.uri() + '/branches/' + branch_id
        branch = None
        try:
            res = self.client.get(uri)
            branch = Branch(self, res)
        except RequestError:
            branch = None

        return branch
            
    def create_branch(self, obj={}):
        uri = self.uri() + '/branches'
        res = self.client.post(uri, obj)

        branch_id = res["_doc"]
        return self.read_branch(branch_id)

        
    # Releases

    def list_releases(self):
        uri = self.uri() + '/releases/'
        res = self.client.get(uri, {})
        return Release.release_map(self, res['rows'])

    def query_releases(self, query, pagination={}):
        uri = self.uri() + '/releases/query'
        res = self.client.post(uri, pagination, query)
        return Release.release_map(self, res['rows'])

    def read_release(self, releaseId):
        uri = self.uri() + '/releases/' + releaseId
        release = None
        try:
            res = self.client.get(uri, {})
            release = Release(self, res)
        except RequestError:
            release = None

        return release

    def start_create_release(self, object={}, source_release_id=None):
        uri = self.uri() + '/releases/create/start'
        params = {}
        if source_release_id:
            params['sourceId'] = source_release_id

        res = self.client.post(uri, params, object)
        return res['_doc']

    @classmethod
    def repository_map(cls, client, data):
        return OrderedDict((repository['_doc'], Repository(client, repository)) for repository in data)
