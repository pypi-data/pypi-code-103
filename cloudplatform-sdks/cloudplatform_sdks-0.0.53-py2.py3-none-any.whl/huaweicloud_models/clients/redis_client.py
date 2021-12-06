from .client import HuaweiClient
from huaweicloudsdkdcs.v2 import DcsClient, CreateInstanceRequest, ListInstancesRequest, DeleteSingleInstanceRequest, \
    UpdateIpWhitelistRequest, Whitelist, ModifyIpWhitelistBody, ShowIpWhitelistRequest
from huaweicloudsdkdcs.v2.region.dcs_region import DcsRegion


class HuaweiRedisClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiRedisClient, self).__init__(*args, **kwargs)

    @property
    def redis_client(self):
        return self.generate_client(DcsClient, DcsRegion)

    def create_redis(self, params=None):
        request = CreateInstanceRequest(params)
        return self.redis_client.create_instance(request)

    def get_redis_info(self, params=None):
        if params:
            request = ListInstancesRequest(instance_id=params)
        else:
            request = ListInstancesRequest()
        return self.redis_client.list_instances(request)

    def delete_redis(self, params=None):
        request = DeleteSingleInstanceRequest(instance_id=params)
        return self.redis_client.delete_single_instance(request)

    def add_white_IP(self, params=None):
        white_lists = list()
        white_list = Whitelist(
            group_name=params['group_name'],
            ip_list=params['ip_list']
        )
        white_lists.append(white_list)
        if params['old_white_list']:
            for white in params['old_white_list']:
                white_lists.append(Whitelist(
                    group_name=white.group_name,
                    ip_list=white.ip_list
                ))
        _body = ModifyIpWhitelistBody(
            enable_whitelist=params['enable_whitelist'],
            whitelist=white_lists
        )
        request = UpdateIpWhitelistRequest(
            instance_id=params['instance_id'],
            body=_body
        )
        return self.redis_client.update_ip_whitelist(request)

    def get_white(self, params=None):
        request = UpdateIpWhitelistRequest(
            instance_id=params
        )
        return self.redis_client.show_ip_whitelist(request)