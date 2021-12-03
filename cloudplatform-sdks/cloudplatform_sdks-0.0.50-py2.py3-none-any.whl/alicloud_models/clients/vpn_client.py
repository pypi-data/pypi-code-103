from .client import AliCloudClient

from aliyunsdkvpc.request.v20160428.CreateVpnGatewayRequest import CreateVpnGatewayRequest
from aliyunsdkvpc.request.v20160428.DeleteVpnGatewayRequest import DeleteVpnGatewayRequest
from aliyunsdkvpc.request.v20160428.ModifyVpnGatewayAttributeRequest import ModifyVpnGatewayAttributeRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnGatewayRequest import DescribeVpnGatewayRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnGatewaysRequest import DescribeVpnGatewaysRequest
from aliyunsdkvpc.request.v20160428.CreateCustomerGatewayRequest import CreateCustomerGatewayRequest
from aliyunsdkvpc.request.v20160428.DeleteCustomerGatewayRequest import DeleteCustomerGatewayRequest
from aliyunsdkvpc.request.v20160428.ModifyCustomerGatewayAttributeRequest import ModifyCustomerGatewayAttributeRequest
from aliyunsdkvpc.request.v20160428.DescribeCustomerGatewayRequest import DescribeCustomerGatewayRequest
from aliyunsdkvpc.request.v20160428.DescribeCustomerGatewaysRequest import DescribeCustomerGatewaysRequest
from aliyunsdkvpc.request.v20160428.CreateVpnConnectionRequest import CreateVpnConnectionRequest
from aliyunsdkvpc.request.v20160428.DeleteVpnConnectionRequest import DeleteVpnConnectionRequest
from aliyunsdkvpc.request.v20160428.ModifyVpnConnectionAttributeRequest import ModifyVpnConnectionAttributeRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnConnectionRequest import DescribeVpnConnectionRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnConnectionsRequest import DescribeVpnConnectionsRequest
from aliyunsdkvpc.request.v20160428.CreateVpnRouteEntryRequest import CreateVpnRouteEntryRequest
from aliyunsdkvpc.request.v20160428.CreateVpnPbrRouteEntryRequest import CreateVpnPbrRouteEntryRequest
from aliyunsdkvpc.request.v20160428.DeleteVpnRouteEntryRequest import DeleteVpnRouteEntryRequest
from aliyunsdkvpc.request.v20160428.DeleteVpnPbrRouteEntryRequest import DeleteVpnPbrRouteEntryRequest
from aliyunsdkvpc.request.v20160428.ModifyVpnRouteEntryWeightRequest import ModifyVpnRouteEntryWeightRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnRouteEntriesRequest import DescribeVpnRouteEntriesRequest
from aliyunsdkvpc.request.v20160428.DescribeVpnPbrRouteEntriesRequest import DescribeVpnPbrRouteEntriesRequest


class VpnGatewayClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(VpnGatewayClient, self).__init__(secret_id, secret_key, region, config, 'vpc')

    def create_vpn_gateway(self, query_params=None, body_params=None):
        return self.do_request(CreateVpnGatewayRequest, query_params, body_params)

    def delete_vpn_gateway(self, query_params=None, body_params=None):
        return self.do_request(DeleteVpnGatewayRequest, query_params, body_params)

    def describe_vpn_gateway(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnGatewayRequest, query_params, body_params)

    def describe_vpns(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnGatewaysRequest, query_params, body_params)

    def modify_vpn_gateway(self, query_params=None, body_params=None):
        return self.do_request(ModifyVpnGatewayAttributeRequest, query_params, body_params)

    def create_customer_gateway(self, query_params=None, body_params=None):
        return self.do_request(CreateCustomerGatewayRequest, query_params, body_params)

    def delete_customer_gateway(self, query_params=None, body_params=None):
        return self.do_request(DeleteCustomerGatewayRequest, query_params, body_params)

    def modify_customer_gateway(self, query_params=None, body_params=None):
        return self.do_request(ModifyCustomerGatewayAttributeRequest, query_params, body_params)

    def describe_customer_gateway(self, query_params=None, body_params=None):
        return self.do_request(DescribeCustomerGatewayRequest, query_params, body_params)

    def describe_customers(self, query_params=None, body_params=None):
        return self.do_request(DescribeCustomerGatewaysRequest, query_params, body_params)

    def create_ipsec_gateway(self, query_params=None, body_params=None):
        return self.do_request(CreateVpnConnectionRequest, query_params, body_params)

    def delete_ipsec_gateway(self, query_params=None, body_params=None):
        return self.do_request(DeleteVpnConnectionRequest, query_params, body_params)

    def modify_ipsec_gateway(self, query_params=None, body_params=None):
        return self.do_request(ModifyVpnConnectionAttributeRequest, query_params, body_params)

    def describe_ipsec_gateway(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnConnectionRequest, query_params, body_params)

    def describe_ipsecs(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnConnectionsRequest, query_params, body_params)

    def create_route(self, query_params=None, body_params=None):
        return self.do_request(CreateVpnRouteEntryRequest, query_params, body_params)

    def create_route_pbr(self, query_params=None, body_params=None):
        return self.do_request(CreateVpnPbrRouteEntryRequest, query_params, body_params)

    def delete_route(self, query_params=None, body_params=None):
        return self.do_request(DeleteVpnRouteEntryRequest, query_params, body_params)

    def delete_route_pbr(self, query_params=None, body_params=None):
        return self.do_request(DeleteVpnPbrRouteEntryRequest, query_params, body_params)

    def modify_route(self, query_params=None, body_params=None):
        return self.do_request(ModifyVpnRouteEntryWeightRequest, query_params, body_params)

    def describe_route(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnRouteEntriesRequest, query_params, body_params)

    def describe_route_pbr(self, query_params=None, body_params=None):
        return self.do_request(DescribeVpnPbrRouteEntriesRequest, query_params, body_params)

