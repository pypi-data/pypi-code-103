import time
from .client import HuaweiClient
from huaweicloudsdkbss.v2 import BssClient, ListPayPerUseCustomerResourcesRequest, QueryResourcesReq, \
    CancelResourcesSubscriptionRequest, UnsubscribeResourcesReq
from huaweicloudsdkbss.v2.region.bss_region import BssRegion


class HuaweiBssClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiBssClient, self).__init__(*args, **kwargs)
        self.region = 'cn-north-1'

    @property
    def bss_client(self):
        return self.generate_global_client(BssClient, BssRegion)

    def list_resources_by_order(self, order_id, default_timeout=300):

        timeout = time.time() + default_timeout
        while not self._query_eip_by_order(order_id) and time.time() < timeout:
            time.sleep(10)
        data = self._query_eip_by_order(order_id)
        if data:
            return data[0].resource_id
        return

    def _query_eip_by_order(self, order_id):
        request = ListPayPerUseCustomerResourcesRequest()
        request.body = QueryResourcesReq(
            only_main_resource=1,
            order_id=order_id
        )
        return self.bss_client.list_pay_per_use_customer_resources(request).data

    def cancel_resource(self, resource_id):  # 退订包年包月资源
        request = CancelResourcesSubscriptionRequest()
        body = [
            resource_id
        ]
        request.body = UnsubscribeResourcesReq(
            unsubscribe_type=1,
            resource_ids=body
        )
        return self.bss_client.cancel_resources_subscription(request)

    def query_resource(self, resource_id):  # 查询包年包月资源
        request = ListPayPerUseCustomerResourcesRequest()
        request.body = QueryResourcesReq(
            only_main_resource=1,
            resource_ids=[resource_id]
        )
        return self.bss_client.list_pay_per_use_customer_resources(request).data


