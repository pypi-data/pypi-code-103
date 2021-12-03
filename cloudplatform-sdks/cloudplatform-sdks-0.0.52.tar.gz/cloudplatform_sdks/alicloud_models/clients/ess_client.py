from .client import AliCloudClient
from aliyunsdkess.request.v20140828.DescribeScalingInstancesRequest import DescribeScalingInstancesRequest
from aliyunsdkess.request.v20140828.DescribeScalingGroupsRequest import DescribeScalingGroupsRequest


class EssClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(EssClient, self).__init__(secret_id, secret_key, region, config, 'ess')

    def describe_scaling_instances(self, query_params=None, body_params=None):
        return self.do_request(DescribeScalingInstancesRequest, query_params, body_params)

    def describe_scaling_groups(self, query_params=None, body_params=None):
        return self.do_request(DescribeScalingGroupsRequest, query_params, body_params)
