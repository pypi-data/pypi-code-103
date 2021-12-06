import time
from .clients import hw_rds_client


class HuaweiRds:

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def name(self):
        return self.object.name

    @property
    def status(self):
        return self.object.status.lower()

    @property
    def flavor(self):
        return self.object.flavor

    @property
    def availability_zone(self):
        return self.object.os_ext_a_zavailability_zone

    @property
    def metadata(self):
        return self.object.metadata

    @property
    def addresses(self):
        return self.object.addresses

    @property
    def volumes(self):
        return self.object.os_extended_volumesvolumes_attached

    @classmethod
    def create(cls, params=None):
        create_response = hw_rds_client.create_instance(body_params=params)
        if not create_response:
            return
        return create_response

    @classmethod
    def mysql_group_type(cls, params=None):
        response = hw_rds_client.mysql_group_type(body_params=params)
        if not response:
            return
        return response

    @classmethod
    def get_mysql_status(cls, params=None):
        response = hw_rds_client.get_mysql_status(body_params=params)
        if not response:
            return
        return response.instances[0].status

    @classmethod
    def delete(cls, params=None):
        delete_response = hw_rds_client.delete_instance(body_params=params)
        if not delete_response:
            return
        return delete_response

    @classmethod
    def describe_instance(cls, params=None):
        response = hw_rds_client.describe_instance(body_params=params)
        if not response:
            return
        return response.instances[0]

    @classmethod
    def list_instances(cls, params=None):
        response = hw_rds_client.list_instances(body_params=params)
        if not response:
            return
        return response
