from .client import AliCloudClient
from aliyunsdkvpc.request.v20160428.CreateNatGatewayRequest import CreateNatGatewayRequest
from aliyunsdkvpc.request.v20160428.DeleteNatGatewayRequest import DeleteNatGatewayRequest
from aliyunsdkvpc.request.v20160428.ModifyNatGatewaySpecRequest import ModifyNatGatewaySpecRequest
from aliyunsdkvpc.request.v20160428.ModifyNatGatewayAttributeRequest import ModifyNatGatewayAttributeRequest
from aliyunsdkvpc.request.v20160428.DescribeNatGatewaysRequest import DescribeNatGatewaysRequest
from aliyunsdkvpc.request.v20160428.AssociateEipAddressRequest import AssociateEipAddressRequest
from aliyunsdkvpc.request.v20160428.UnassociateEipAddressRequest import UnassociateEipAddressRequest
from aliyunsdkvpc.request.v20160428.DescribeVpcAttributeRequest import DescribeVpcAttributeRequest
from aliyunsdkvpc.request.v20160428.CreateSnatEntryRequest import CreateSnatEntryRequest
from aliyunsdkvpc.request.v20160428.DescribeSnatTableEntriesRequest import DescribeSnatTableEntriesRequest
from aliyunsdkvpc.request.v20160428.DeleteSnatEntryRequest import DeleteSnatEntryRequest
from aliyunsdkvpc.request.v20160428.CreateForwardEntryRequest import CreateForwardEntryRequest
from aliyunsdkvpc.request.v20160428.DescribeForwardTableEntriesRequest import DescribeForwardTableEntriesRequest
from aliyunsdkvpc.request.v20160428.DeleteForwardEntryRequest import DeleteForwardEntryRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

class NatClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(NatClient, self).__init__(secret_id, secret_key, region, config, 'vpc')

    def create_nat(self, query_params=None, body_params=None):
        return self.do_request(CreateNatGatewayRequest, query_params, body_params)

    def delete_nat(self, query_params=None, body_params=None):
        return self.do_request(DeleteNatGatewayRequest, query_params, body_params)

    def modify_nat_spec(self, query_params=None, body_params=None):
        return self.do_request(ModifyNatGatewaySpecRequest, query_params, body_params)

    def modify_nat_attrs(self, query_params=None, body_params=None):
        return self.do_request(ModifyNatGatewayAttributeRequest, query_params, body_params)

    def describe_nats(self, query_params=None, body_params=None):
        return self.do_request(DescribeNatGatewaysRequest, query_params, body_params)

    def bound_eip(self, query_params=None, body_params=None):
        return self.do_request(AssociateEipAddressRequest, query_params, body_params)

    def unbound_eip(self, query_params=None, body_params=None):
        return self.do_request(UnassociateEipAddressRequest, query_params, body_params)

    def describe_vpc(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpcAttributeRequest, query_params, body_params)

    def create_snat(self, query_params=None, body_params=None):
        return self.do_request(CreateSnatEntryRequest, query_params, body_params)

    def describe_snat(self, query_params=None, body_params=None):
        return self.do_request(DescribeSnatTableEntriesRequest, query_params, body_params)

    def delete_snat(self, query_params=None, body_params=None):
        return self.do_request(DeleteSnatEntryRequest, query_params, body_params)

    def create_dnat(self, query_params=None, body_params=None):
        return self.do_request(CreateForwardEntryRequest, query_params, body_params)

    def describe_dnat(self, query_params=None, body_params=None):
        return self.do_request(DescribeForwardTableEntriesRequest, query_params, body_params)

    def delete_dnat(self, query_params=None, body_params=None):
        return self.do_request(DeleteForwardEntryRequest, query_params, body_params)


class EcsClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(EcsClient, self).__init__(secret_id, secret_key, region, config, 'ecs')

    def get_ecs(self, query_params=None, body_params=None):
        return self.do_request(DescribeInstancesRequest, query_params, body_params)