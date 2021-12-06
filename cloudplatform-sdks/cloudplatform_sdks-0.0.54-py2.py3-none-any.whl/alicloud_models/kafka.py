import json
from .clients import kafka_client, order_client


class AliKafka:
    """
    {
        "DeployType": 4,
        "SslEndPoint": "139.196.201.204:9093,139.224.80.27:9093,47.100.78.6:9093",
        "EipMax": 1,
        "ZoneId": "zonea",
        "InstanceId": "alikafka_post-cn-7pp2db31801k",
        "SpecType": "normal",
        "IoMax": 20,
        "VSwitchId": "vsw-uf6ktvvykw5zlq2vt8er5",
        "CreateTime": 1632791710000,
        "AllConfig": "{\"enable.vpc_sasl_ssl\":\"false\",\"kafka.log.retention.hours\":\"72\",\"kafka.offsets.retention.minutes\":\"10080\",\"enable.acl\":\"false\",\"enable.compact\":\"true\",\"kafka.message.max.bytes\":\"1048576\"}",
        "EndPoint": "10.128.0.51:9092,10.128.0.53:9092,10.128.0.52:9092",
        "SecurityGroup": "sg-uf6a9048z57theabnmse",
        "UpgradeServiceDetailInfo": {
            "Current2OpenSourceVersion": "2.2.0"
        },
        "Name": "alikafka_post-cn-7pp2db31801k",
        "DiskType": 0,
        "VpcId": "vpc-uf6mnlufuqxforawqcpn7",
        "ServiceStatus": 5,
        "PaidType": 1,
        "ExpiredTime": 1948324509000,
        "MsgRetain": 72,
        "DiskSize": 500,
        "TopicNumLimit": 50,
        "RegionId": "cn-shanghai",
        "Tags": {
            "TagVO": []
    }
    """

    def __init__(self, object):
        self.object = object

    @classmethod
    def get(cls, external_id):
        res = kafka_client.get_kafka({"InstanceId.1": external_id})
        objs = res['InstanceList']['InstanceVO']
        if objs:
            return cls(objs[0])
        return None

    def fresh(self):
        self.object = self.get(self.external_id).object

    @classmethod
    def list(cls):
        res = kafka_client.get_kafka()
        objs = res['InstanceList']['InstanceVO']
        return [cls(obj) for obj in objs]

    @classmethod
    def create(cls, params, pay_mode='post_pay_order'):
        """
        pay_mode = post_pay_order or pre_pay_order
        """
        if pay_mode == 'post_pay_order':
            res = kafka_client.create_kafka_with_post_pay(params)
        else:
            res = kafka_client.create_kafka_with_pre_pay(params)
        order = order_client.get_details({"OrderId": res['OrderId']})
        instance_ids = json.loads(order['Data']['OrderList']['Order'][0]['InstanceIDs'])
        return instance_ids[0]

    @staticmethod
    def start(params):
        res = kafka_client.start_kafka(params)
        return res

    def delete(self):
        kafka_client.delete_kafka({"InstanceId": self.external_id, "ForceDeleteInstance": "true"})

    def get_security_ips(self):
        res = kafka_client.get_while_list({"InstanceId": self.external_id})
        vpc_ips = res['AllowedList']['VpcList'][0]['AllowedIpList']
        if res['AllowedList'].get('InternetList'):
            internet_ips = res['AllowedList']['InternetList'][0]['AllowedIpList']
        else:
            internet_ips = []
        return {
            "vpc_allowed_ips": vpc_ips,
            "internet_allowed_ips": internet_ips
        }

    def update_security_ips(self, ip):
        # vpc
        params = {
            "UpdateType": "add",
            "PortRange": '9092/9092',
            "AllowedListType": 'vpc',
            "AllowedListIp": ip,
            "InstanceId": self.external_id
        }
        kafka_client.update_while_list(params)
        if self.deploy_type == 'eip/vpc':
            params.update({
                "PortRange": '9093/9093',
                "AllowedListType": 'internet',
            })
            kafka_client.update_while_list(params)

    @property
    def external_id(self):
        return self.object.get('InstanceId')

    @property
    def external_name(self):
        return self.object.get('Name')

    @property
    def deploy_type(self):
        """
        4：公网/VPC实例
        5：VPC实例
        """
        mapper = {
            4: "eip/vpc",
            5: "vpc"
        }
        return mapper[self.object.get('DeployType')]

    @property
    def ssl_end_point(self):
        return self.object.get('SslEndPoint')

    @property
    def eip_max(self):
        return self.object.get('EipMax')

    @property
    def zone_id(self):
        return self.object.get('ZoneId')

    @property
    def spec_type(self):
        return self.object.get('SpecType')

    @property
    def io_max(self):
        return self.object.get('IoMax')

    @property
    def vswitch_id(self):
        return self.object.get('VSwitchId')

    @property
    def all_config(self):
        return self.object.get('AllConfig')

    @property
    def end_point(self):
        return self.object.get('EndPoint')

    @property
    def security_group(self):
        return self.object.get('SecurityGroup')

    @property
    def upgrade_service_detail_info(self):
        return self.object.get('UpgradeServiceDetailInfo')

    @property
    def version(self):
        return self.upgrade_service_detail_info['Current2OpenSourceVersion']

    @property
    def disk_type(self):
        """
        0：高效云盘
        1：SSD
        """
        mapper = {
            0: "Cloud Disk",
            1: "SSD"
        }
        return mapper[self.object.get('DiskType')]

    @property
    def vpc_id(self):
        return self.object.get('VpcId')

    @property
    def status(self):
        """
        0：待部署
        1：部署中
        5：服务中
        15：已过期
        """
        mapper = {
            "0": "pending",
            "1": "creating",
            "2": "starting",
            "5": "running",
            "11": "configuring",
            "15": "lost",
        }
        res = mapper.get(str(self.object.get('ServiceStatus')))
        return res or "unknow"

    @property
    def paid_type(self):
        """
        0：预付费
        1：后付费
        """
        mapper = {
            0: "prePay",
            1: "postPay"
        }
        return self.object.get('PaidType')

    @property
    def msg_retain(self):
        """
        unit: hour
        """
        return self.object.get('MsgRetain')

    @property
    def disk_size(self):
        """
        unit: GB
        """
        return self.object.get('DiskSize')

    @property
    def topic_num_limit(self):
        return self.object.get('TopicNumLimit')

    @property
    def region_id(self):
        return self.object.get('RegionId')

    @property
    def tags(self):
        return self.object.get('Tags')

    @property
    def attributes(self):
        return {
            "external_id": self.external_id,
            "external_name": self.external_name,
            "deploy_type": self.deploy_type,
            "ssl_end_point": self.ssl_end_point,
            "eip_max": self.eip_max,
            "zone_id": self.zone_id,
            "spec_type": self.spec_type,
            "io_max": self.io_max,
            "vswitch_id": self.vswitch_id,
            "all_config": self.all_config,
            "end_point": self.end_point,
            "security_group": self.security_group,
            "upgrade_service_detail_info": self.upgrade_service_detail_info,
            "version": self.version,
            "disk_type": self.disk_type,
            "vpc_id": self.vpc_id,
            "status": self.status,
            "paid_type": self.paid_type,
            "msg_retain": self.msg_retain,
            "disk_size": self.disk_size,
            "topic_num_limit": self.topic_num_limit,
            "region_id": self.region_id,
            "tags": self.tags,
        }

    def __repr__(self):
        return "<AliKafka object:{}>".format(self.external_id)
