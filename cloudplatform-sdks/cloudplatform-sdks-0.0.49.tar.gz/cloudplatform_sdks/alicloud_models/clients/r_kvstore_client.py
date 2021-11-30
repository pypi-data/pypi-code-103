from .client import AliCloudClient
from aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkr_kvstore.request.v20150101.DescribeDBInstanceNetInfoRequest import DescribeDBInstanceNetInfoRequest
from aliyunsdkr_kvstore.request.v20150101.DescribeSecurityIpsRequest import DescribeSecurityIpsRequest
from aliyunsdkr_kvstore.request.v20150101.DescribeInstanceAttributeRequest import DescribeInstanceAttributeRequest
from aliyunsdkr_kvstore.request.v20150101.DescribeInstanceAutoRenewalAttributeRequest import \
    DescribeInstanceAutoRenewalAttributeRequest


class RKvstoreClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(RKvstoreClient, self).__init__(secret_id, secret_key, region, config, 'r-kvstore')

    def describe_instances(self, query_params=None, body_params=None):
        return self.do_request(DescribeInstancesRequest, query_params, body_params)

    def describe_instance_netinfo(self, query_params=None, body_params=None):
        return self.do_request(DescribeDBInstanceNetInfoRequest, query_params, body_params)

    def describe_security_ips(self, query_params=None, body_params=None):
        return self.do_request(DescribeSecurityIpsRequest, query_params, body_params)

    def describe_instance_attribute(self, query_params=None, body_params=None):
        return self.do_request(DescribeInstanceAttributeRequest, query_params, body_params)

    def describe_instance_auto_renewal_attribute(self, query_params=None, body_params=None):
        return self.do_request(DescribeInstanceAutoRenewalAttributeRequest, query_params, body_params)
