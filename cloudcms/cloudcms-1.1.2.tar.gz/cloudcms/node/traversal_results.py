from .base_node import BaseNode

class TraversalResults(object):
    
    def __init__(self):
        self.nodes = []
        self.associations = []
    
    @classmethod
    def parse(cls, response, branch):
        result = TraversalResults()
        nodes_obj = response['nodes']

        for node_obj in nodes_obj.values():
            node = BaseNode.build_node(branch, node_obj)
            result.nodes.append(node)
        
        associations_obj = response['associations']
        for association_obj in associations_obj.values():
            association = BaseNode.build_node(branch, association_obj, force_association=True)
            result.associations.append(association)
        
        return result
