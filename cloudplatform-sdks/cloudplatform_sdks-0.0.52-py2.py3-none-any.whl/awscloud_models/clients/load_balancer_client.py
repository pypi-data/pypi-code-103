# -*- coding: utf-8 -*-
# Copyright (c) 2021 Qianyun, Inc. All rights reserved.


from .client import AWSCloudClient


class LoadBalancerClient(AWSCloudClient):
    """负载均衡Client"""
    def __init__(self, secret_id, secret_key, region, config):
        super(LoadBalancerClient, self).__init__(secret_id, secret_key, region, config, 'elbv2')

    def describe_target_group(self, target_group_arns=[]):
        """
        获取目标群组

        :param target_group_arns: List
        :return: Dict
        """
        return self.client.describe_target_groups(
            TargetGroupArns=target_group_arns
        )

    def describe_listener(self, load_balancer_arn, listener_arns=[]):
        """
        获取监听器

        :param load_balancer_arn: String 负载均衡ARN
        :param listener_arns: list 监听器ARN列表
        :return:
        """
        if listener_arns:
            return self.client.describe_listeners(
                ListenerArns=listener_arns,
            )
        else:
            return self.client.describe_listeners(
                LoadBalancerArn=load_balancer_arn,
            )

    def describe_target_health(self, target_group_arn):
        return self.client.describe_target_health(
            TargetGroupArn=target_group_arn
        )
