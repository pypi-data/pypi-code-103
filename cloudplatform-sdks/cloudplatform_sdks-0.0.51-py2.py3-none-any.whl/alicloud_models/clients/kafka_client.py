import json
from .client import AliCloudClient
from aliyunsdkcore.request import CommonRequest


class KafkaClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region, config):
        super(KafkaClient, self).__init__(secret_id, secret_key, region, config, 'alikafka')

    def get_domain(self):
        return 'alikafka.{}.aliyuncs.com'.format(self.region)

    def do_request(self, action, query_params=None, body_params=None):
        req = CommonRequest()
        req.set_accept_format('json')
        req.set_domain(self.get_domain())
        req.set_method('POST')
        req.set_protocol_type('https')
        req.set_version('2019-09-16')
        req.set_action_name(action)
        if query_params:
            for k, v in query_params.items():
                req.add_query_param(k, v)
        if body_params:
            for k, v in body_params.items():
                req.add_body_params(k, v)
        try:
            res = self.client.do_action_with_exception(req)
        except Exception as e:
            raise e
        return json.loads(res)

    def create_kafka_with_post_pay(self, query_params=None, body_params=None):
        return self.do_request("CreatePostPayOrder", query_params, body_params)

    def create_kafka_with_pre_pay(self, query_params=None, body_params=None):
        return self.do_request("CreatePrePayOrder", query_params, body_params)

    def start_kafka(self, query_params=None, body_params=None):
        return self.do_request("StartInstance", query_params, body_params)

    def get_kafka(self, query_params=None, body_params=None):
        return self.do_request("GetInstanceList", query_params, body_params)

    def delete_kafka(self, query_params=None, body_params=None):
        return self.do_request("ReleaseInstance", query_params, body_params)

    def get_while_list(self, query_params=None, body_params=None):
        return self.do_request("GetAllowedIpList", query_params, body_params)

    def update_while_list(self, query_params=None, body_params=None):
        return self.do_request("UpdateAllowedIp", query_params, body_params)

    def update_kafka(self, query_params=None, body_params=None):
        return self.do_request("UpdateInstanceConfig", query_params, body_params)
