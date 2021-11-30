import json
from collections import OrderedDict
from ..repository.repository_object import RepositoryObject
from ..error import RequestError
from ..node.base_node import BaseNode

class Branch(RepositoryObject):

    def __init__(self, repository, data):
        super(Branch, self).__init__(repository, data)

    def uri(self):
        return '%s/branches/%s' % (self.repository.uri(), self._doc) 

    def is_master(self):
        return self.data['type'] == 'MASTER'
    
    def root_node(self):
        return self.read_node('root')

    def reset(self, changeset_id):
        uri = self.uri() + '/reset/start'
        params = {
            'id': changeset_id
        }

        res = self.client.post(uri, params, {})
        return res['_doc']


    def read_node(self, node_id):
        uri = self.uri() + "/nodes/" + node_id
        node = None
        try:
            res = self.client.get(uri)
            node = BaseNode.build_node(self, res)
        except RequestError:
            node = None

        return node
    
    def query_nodes(self, query, pagination={}):
        uri = self.uri() + "/nodes/query"

        res = self.client.post(uri, params=pagination, data=query)
        return BaseNode.node_map(self, res['rows'])

    def search_nodes(self, text, pagination={}):
        uri = self.uri() + '/nodes/search'
        params = pagination
        params['text'] = text

        res = self.client.get(uri, params)
        return BaseNode.node_map(self, res['rows'])

    def find_nodes(self, config, pagination={}):
        uri = self.uri() + "/nodes/find"

        res = self.client.post(uri, params=pagination, data=config)
        return BaseNode.node_map(self, res['rows'])

    def create_node(self, obj={}, options={}):
        uri = self.uri() + "/nodes"

        params = {}
        params['rootNodeId'] = options.get('rootNodeId') or 'root'
        params['associationType'] = options.get('associationType') or 'a:child'

        if 'parentFolderPath' in options:
            params['parentFolderPath'] = options['parentFolderPath']
        elif 'folderPath' in options:
            params['parentFolderPath'] = options['folderPath']
        elif 'folderpath' in options:
            params['parentFolderPath'] = options['folderpath']  
        
        if 'filePath' in options:
            params['filePath'] = options['filePath']
        elif 'filepath' in options:
            params['filePath'] = options['filepath']

        res = self.client.post(uri, params=params, data=obj)
        node_id = res['_doc']

        return self.read_node(node_id)

    def delete_nodes(self, node_ids):
        uri = self.uri() + '/nodes/delete'
        return self.client.post(uri, data=node_ids)

    def graphql_query(self, query, operation_name=None, variables={}):
        uri = self.uri() + "/graphql"
        
        params = {}
        params['query'] = query

        if variables is not None:
            params['variables'] = variables
        
        if operation_name is not None:
            params['operation_name'] = operation_name

        return self.client.get(uri, params)

    def graphql_schema(self):
        uri = self.uri() + "/graphql/schema"
        return self.client.request("GET", uri, output_json=False)

    @classmethod
    def branch_map(cls, repository, data):
        return OrderedDict((branch['_doc'], Branch(repository, branch)) for branch in data)