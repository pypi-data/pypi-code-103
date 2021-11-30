from ..node import BaseNode
from ..support import QName
from collections import OrderedDict
from .directionality import Directionality

class Association(BaseNode):

    def __init__(self, branch, data):
        super(Association, self).__init__(branch, data)

    def get_source_type_qname(self):
        return QName.create(qname=self.data['source_type'])

    def set_source_type_qname(self, source_type_qname):
        self.data['source_type'] = str(source_type_qname)

    def get_source_node_id(self):
        return self.data['source']

    def set_source_node_id(self, source_node_id):
        self.data['source'] = source_node_id

    def get_target_type_qname(self):
        return QName.create(qname=self.data['target_type'])

    def set_target_type_qname(self, target_type_qname):
        self.data['target_type'] = str(target_type_qname)

    def get_target_node_id(self):
        return self.data['target']

    def set_target_node_id(self, target_node_id):
        self.data['target'] = target_node_id

    def get_directionality(self):
        dir_str = self.data['directionality']
        return Directionality[dir_str]

    def set_directionality(self, directionality):
        self.data['directionality'] = str(directionality)


    def read_source_node(self):
        node_id = self.get_source_node_id()
        return self.branch.read_node(node_id)

    def read_target_node(self):
        node_id = self.get_target_node_id()
        return self.branch.read_node(node_id)

    @classmethod
    def association_map (cls, branch, data):
        return OrderedDict((association['_doc'], Association(branch, association)) for association in data)