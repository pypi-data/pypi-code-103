# -*- coding: utf-8 -*-
# Copyright (c) 2021 Qianyun, Inc. All rights reserved.


import boto3


class AWSCloudClient(object):
    def __init__(self, secret_id, secret_key, region, config, server_name):
        """
        实例化AWS Client

        :param secret_id: string AWS 密钥ID
        :param secret_key: string AWS 密钥
        :param region: string AWS 地区
        :param config: 未知
        :param server_name: string AWS连接的服务名称
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.config = config
        self.server_name = server_name
        self.client = self._client()

    def _client(self):
        boto3.setup_default_session(aws_access_key_id=self.secret_id,
                                    aws_secret_access_key=self.secret_key,
                                    region_name=self.region)

        client = boto3.client(self.server_name)
        return client
