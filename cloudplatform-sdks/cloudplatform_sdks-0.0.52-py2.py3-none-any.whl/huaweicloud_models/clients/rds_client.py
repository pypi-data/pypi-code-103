from .client import HuaweiClient
from huaweicloudsdkrds.v3.region.rds_region import RdsRegion
from huaweicloudsdkrds.v3 import *


class HuaweiRdsClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiRdsClient, self).__init__(*args, **kwargs)

    @property
    def rds_client(self):
        return self.generate_client(RdsClient, RdsRegion)

    def create_instance(self, body_params=None):
        request = CreateInstanceRequest(body=body_params)
        return self.rds_client.create_instance(request)

    def mysql_group_type(self):
        request = ListFlavorsRequest()
        request.database_name = "MySQL"
        return self.rds_client.list_flavors(request)

    def get_mysql_status(self, body_params=None):
        request = ListInstancesRequest()
        request.id = body_params.get("id")
        request.datastore_type = "MySQL"
        return self.rds_client.list_instances(request)

    def delete_instance(self, body_params=None):
        request = DeleteInstanceRequest()
        request.instance_id = body_params.get("instance_id")
        return self.rds_client.delete_instance(request)

    def describe_instance(self, body_params=None):
        request = ListInstancesRequest()
        request.id = body_params.get("id")
        request.datastore_type = "MySQL"
        return self.rds_client.list_instances(request)

    def list_instances(self, body_params=None):
        request = ListInstancesRequest()
        request.datastore_type = "MySQL"
        return self.rds_client.list_instances(request)