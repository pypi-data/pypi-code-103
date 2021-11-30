from .base_node import BaseNode
from ..association import Association, Direction, Directionality
from ..support import QName
from .traversal_results import TraversalResults

class Node(BaseNode):

    def __init__(self, branch, data):
        super(Node, self).__init__(branch, data)

    # Associations
    def associations(self, pagination={}, direction=Direction.ANY, association_type_qname=None):
        uri = self.uri() + '/associations'
        params = {}
        params['direction'] = str(direction)

        if association_type_qname is not None:
            params['type'] = str(association_type_qname)

        response = self.client.get(uri, params=params)
        rows = response['rows']
        return Association.association_map(self.branch, rows)
    
    def associate(self, other_node, association_type_qname, data={}, directionality=Directionality.DIRECTED):
        uri = self.uri() + '/associate'
        params = {}
        params['node'] = other_node._doc
        params['type'] = str(association_type_qname)
        if directionality is not Directionality.DIRECTED:
            params['directionality'] = str(directionality)

        response1 = self.client.post(uri, params, data)
        association_id = response1['_doc']

        # Read back assocation object
        read_back_uri = self.branch.uri() + '/nodes/' + association_id
        response2 = self.client.get(read_back_uri)
        
        return Association(self.branch, response2)

    def unassociate(self, other_node, association_type_qname, directionality=Directionality.DIRECTED):
        uri = self.uri() + '/unassociate'
        params = {}
        params['node'] = other_node._doc
        params['type'] = str(association_type_qname)
        if directionality is not Directionality.DIRECTED:
            params['directionality'] = str(directionality)
        
        self.client.post(uri, params)
    
    def associate_of(self, source_node, association_type_qname, data={}):
        return source_node.associate(self, association_type_qname, data=data)

    def child_of(self, source_node):
        return self.associate_of(source_node, QName.create('a:child'))


    def file_folder_tree(self, base_path=None, leaf_paths=[], depth=-1, include_properties=True, containers_only=False, query={}):
        uri = self.uri() + '/tree'
        params = {}
        if base_path is not None:
            params['base'] = base_path
        
        if leaf_paths is not None and len(leaf_paths) > 0:
            leafs_param = ','.join(leaf_path for leaf_path in leaf_paths)
            params['leaf'] = leafs_param

        if depth > -1:
            params['depth'] = depth
        
        if include_properties:
            params['properties'] = include_properties
        
        if containers_only:
            params['containers'] = containers_only
        
        result = self.client.post(uri, params)
        return result
    
    def list_children(self, pagination={}):
        uri = self.uri() + '/children'
        response = self.client.get(uri, pagination)
        return BaseNode.node_map(self.branch, response['rows'])
    
    def list_relatives(self, type_qname, direction, pagination={}):
        uri = self.uri() + '/relatives'
        params = pagination
        params['type'] = str(type_qname)
        params['direction'] = str(direction)

        response = self.client.get(uri, params)
        return BaseNode.node_map(self.branch, response['rows'])

    def query_relatives(self, type_qname, direction, query, pagination={}):
        uri = self.uri() + '/relatives/query'
        params = pagination
        params['type'] = str(type_qname)
        params['direction'] = str(direction)

        response = self.client.post(uri, params, query)
        return BaseNode.node_map(self.branch, response['rows'])

    def traverse(self, traverse_config):
        uri = self.uri() + '/traverse'

        body = { 'traverse': traverse_config }
        response = self.client.post(uri, data=body)
        results = TraversalResults.parse(response, self.branch)
        return results
    
    # Paths
    def resolve_path(self):
        uri = self.uri() + '/path'
        params = { 'rootNodeId': 'r:root' }

        response = self.client.get(uri, params)
        return response.path

    def resolve_paths(self):
        uri = self.uri() + '/paths'
        response = self.client.get(uri, {})

        return response.paths

    # Translations
    def create_translation(self, locale, edition, obj):
        uri = self.uri() + '/i18n'
        params = {
            'locale': locale,
            'edition': edition
        }

        response1 = self.client.post(uri, params, obj)
        node_id = response1['_doc']
        
        # Read back node
        return self.branch.read_node(node_id)
    
    def get_translation_editions(self):
        uri = self.uri() + '/i18n/editions'
        response = self.client.get(uri)

        return response['editions']
    
    def get_translation_locales(self, edition):
        uri = self.uri() + '/i18n/locales'
        params = { 'edition': edition }

        response = self.client.get(uri, params)
        return response['locales']
    
    def read_translation(self, locale, edition=None):
        uri = self.uri() + '/i18n'
        params = {}
        params['locale'] = locale

        if edition is not None:
            params['edition'] = edition
        
        response = self.client.get(uri, params)
        return Node(self.branch, response)
