from .client import AliCloudClient
from aliyunsdkvpc.request.v20160428.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkvpc.request.v20160428.DescribeVpcAttributeRequest import DescribeVpcAttributeRequest
from aliyunsdkvpc.request.v20160428.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkvpc.request.v20160428.DescribeVSwitchAttributesRequest import DescribeVSwitchAttributesRequest
from aliyunsdkvpc.request.v20160428.DescribeEipAddressesRequest import DescribeEipAddressesRequest


class VpcClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(VpcClient, self).__init__(secret_id, secret_key, region, config, 'vpc')

    def describe_vpcs(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpcsRequest, query_params, body_params)

    def describe_vpc_attribute(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpcAttributeRequest, query_params, body_params)

    def describe_vswitches(self, query_params=None, body_params=None):
        return self.do_request(DescribeVSwitchesRequest, query_params, body_params)

    def describe_vswitch_attributes(self, query_params=None, body_params=None):
        return self.do_request(DescribeVSwitchAttributesRequest, query_params, body_params)

    def describe_eip_address(self, query_params=None, body_params=None):
        return self.do_request(DescribeEipAddressesRequest, query_params, body_params)
