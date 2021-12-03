from .client import AliCloudClient
from aliyunsdkcs.request.v20151215.DescribeClustersRequest import DescribeClustersRequest
from aliyunsdkcs.request.v20151215.DescribeClusterDetailRequest import DescribeClusterDetailRequest


class CsClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(CsClient, self).__init__(secret_id, secret_key, region, config, 'cs')

    def describe_clusters(self, query_params=None, body_params=None):
        return self.do_request(DescribeClustersRequest, query_params, body_params)

    def describe_detail_clusters(self, query_params=None, body_params=None):
        return self.do_request(DescribeClusterDetailRequest, query_params, body_params)

