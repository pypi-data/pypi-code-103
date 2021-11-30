from collections import OrderedDict
from ..repository.repository_object import RepositoryObject
from ..attachment import Attachment

class BaseNode(RepositoryObject):

    def __init__(self, branch, data):
            super(BaseNode, self).__init__(branch.repository, data)
            
            self.branch_id = branch._doc
            self.branch = branch

    def uri(self):
        return '%s/nodes/%s' % (self.branch.uri(), self._doc)

    def refresh(self):
        uri = self.uri() + '/refresh'
        return self.client.post(uri)

    def change_node_qname(self, new_qname):
        uri = self.uri() + '/change_qname'
        params = {
            'qname': new_qname
        }

        return self.client.post(uri, params, {})

    # Attachments

    def download_attachment(self, attachment_id='default'):
        uri = self.uri() + '/attachments/' + attachment_id

        return self.client.get(uri, output_json=False)

    def upload_attachment(self, file, content_type, attachment_id='default', filename=None):
        uri = self.uri() + '/attachments/' + attachment_id
        name = filename if filename else attachment_id

        return self.client.upload(uri, name, file, content_type)

    def delete_attachment(self, attachment_id='default'):
        uri = self.uri() + '/attachments/' + attachment_id
        return self.client.delete(uri)
    
    def list_attachments(self):
        uri = self.uri() + '/attachments'
        response = self.client.get(uri)
        return Attachment.attachments_map(self, response['rows'])

    # Features

    def get_feature_ids(self):
        features_obj = self.data['_features']
        return features_obj.keys()

    def get_feature(self, feature_id):
        features_obj = self.data['_features']
        return features_obj.get(feature_id)

    def has_feature(self, feature_id):
        features_obj = self.data['_features']
        return feature_id in features_obj

    def add_feature(self, feature_id, feature_config):
        uri = self.uri() + '/features/' + feature_id
        self.client.post(uri, data=feature_config)
        self.reload()
    
    def remove_feature(self, feature_id):
        uri = self.uri() + '/features/' + feature_id
        self.client.delete(uri)
        self.reload()

    # Versions

    def read_version(self, changesetId, options={}):
        uri = self.uri() + '/versions/' + changesetId

        response = self.client.get(uri, options)
        return BaseNode.build_node(self.branch, response)

    def list_versions(self, options={}, pagination={}):
        uri = self.uri() + '/versions'

        params = {
            **options,
            **pagination
        }

        response = self.client.get(uri, params)
        return BaseNode.version_map(self.branch, response['rows'])

    def restore_version(self, changesetId):
        uri = self.uri() + '/versions/' + changesetId + '/restore'
        response = self.client.post(uri, {}, {})

        return BaseNode.build_node(self.branch, response)

    @classmethod
    def node_map (cls, branch, data):
        return OrderedDict((node['_doc'], cls.build_node(branch, node)) for node in data)

    @classmethod
    def version_map (cls, branch, data):
        return OrderedDict((node['_changesetId'], cls.build_node(branch, node)) for node in data)

    @classmethod
    def build_node (cls, branch, data, force_association=False):
        if force_association or ('is_association' in data and data['is_association']):
            from ..association import Association
            return Association(branch, data)
        else:
            from . import Node
            return Node(branch, data)