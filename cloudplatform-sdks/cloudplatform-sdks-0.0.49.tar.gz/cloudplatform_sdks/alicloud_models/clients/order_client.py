from .client import AliCloudClient

from aliyunsdkbssopenapi.request.v20171214.GetOrderDetailRequest import GetOrderDetailRequest


class OrderClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(OrderClient, self).__init__(secret_id, secret_key, region, config, 'business')

    def get_details(self, query_params=None, body_params=None):
        """
        {
            "RequestId": "32D2A046-36EE-5AEA-96D3-CA25F782E9F9",
            "Message": "Successful!",
            "Data": {
                "OrderList": {
                    "Order": [
                        {
                            "AfterTaxAmount": 0,
                            "ProductCode": "alikafka",
                            "SubOrderId": "211059788270709",
                            "Config": "",
                            "CreateTime": "2021-10-11T02:11:16Z",
                            "ProductType": "alikafka_post",
                            "Quantity": 1,
                            "PaymentTime": "2021-10-11T02:11:16Z",
                            "OrderId": "211059788270709",
                            "UsageEndTime": "2121-10-11T16:00:00Z",
                            "SubscriptionType": "PayAsYouGo",
                            "PretaxGrossAmount": 0,
                            "OrderType": "New",
                            "PretaxAmount": 0,
                            "OrderSubType": "ProductSubOrder",
                            "Currency": "CNY",
                            "CommodityCode": "alikafka_post",
                            "Region": "cn-shanghai",
                            "UsageStartTime": "2021-10-11T02:11:16Z",
                            "OriginalConfig": "topic_quata:[topic_quata:50;]disk_type:[disk_type:0;]disk_size:[disk_size:500;]msg_retain:[msg_retain:72;]region:[region:cn-shanghai;]IO_max:[IO_max:20;]spec_type:[spec_type:normal;]vpc_deploy:[vpc_deploy:true;]",
                            "InstanceIDs": "[\"alikafka_post-cn-zvp2dz8ar00g\"]",
                            "PaymentStatus": "Paid",
                            "PretaxAmountLocal": 0
                        }
                    ]
                }
            },
            "Code": "Success",
            "Success": true
        }
        """
        return self.do_request(GetOrderDetailRequest, query_params, body_params)

