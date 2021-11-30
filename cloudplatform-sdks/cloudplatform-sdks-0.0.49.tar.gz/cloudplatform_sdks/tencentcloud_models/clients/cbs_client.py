from .client import TencentClient
from tencentcloud.cbs.v20170312 import cbs_client, models


class CbsClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(CbsClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "cbs.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = cbs_client.CbsClient(self.cred, self.region, self.clientProfile)

    def describe_volume(self, **kwargs):
        req = models.DescribeDisksRequest()
        return self.do_request(self.client.DescribeDisks, req, **kwargs)
