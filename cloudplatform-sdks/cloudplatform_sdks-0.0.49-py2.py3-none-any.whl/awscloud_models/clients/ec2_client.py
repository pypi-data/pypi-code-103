# -*- coding: utf-8 -*-
# Copyright (c) 2021 Qianyun, Inc. All rights reserved.


from .client import AWSCloudClient


class Ec2Client(AWSCloudClient):
    """负载均衡Client"""
    def __init__(self, secret_id, secret_key, region, config):
        super(Ec2Client, self).__init__(secret_id, secret_key, region, config, 'ec2')

    def instance_list(self, ids=[]):
        """
        获取实例列表

        :return: Dict
        """
        return self.client.describe_instances(
            InstanceIds=ids
        )
