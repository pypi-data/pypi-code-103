# -*- coding: UTF-8 -*-
# @Time : 2021/12/3 下午7:05 
# @Author : 刘洪波
import pulsar_mq
import rabbitmq

"""rabbitmq 和 pulsar互相通信"""


class Interconnect(object):
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, pulsar_url):
        """
        rabbitmq 和 pulsar 连接
        :param rabbitmq_host: rabbitmq 的 host
        :param rabbitmq_port: rabbitmq 的 port
        :param rabbitmq_username: rabbitmq 的 username
        :param rabbitmq_password: rabbitmq 的 password
        :param pulsar_url: pulsar的url
        """
        self.rabbitmq_connect = rabbitmq.connect(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password)
        self.client = pulsar_mq.client(pulsar_url)

    def rabbitmq_to_pulsar(self, task, pulsar_topic, rabbitmq_exchange, rabbitmq_routing_key,
                           rabbitmq_thread_count=None, _async=True, send_callback=None, logger=None):
        """
        1. 订阅rabbitmq
        2. 处理消费的数据
        3. 将处理后的数据 发送到 pulsar
        :param task:  该函数是处理消费的数据
        :param pulsar_topic:
        :param rabbitmq_exchange:
        :param rabbitmq_routing_key:
        :param rabbitmq_thread_count:
        :param _async:  pulsar是否异步发送
        :param send_callback: pulsar异步发送时的回调函数
        :param logger: 日志收集器
        :return:
        """
        producer = self.client.create_producer(pulsar_topic)

        def callback(msg):
            result = task(msg)
            if result:
                producer.send(result, _async, send_callback, logger)

        self.rabbitmq_connect.receive(rabbitmq_exchange, rabbitmq_routing_key, callback, rabbitmq_thread_count)

    def pulsar_to_rabbitmq(self, task, pulsar_topic, pulsar_consumer_name, rabbitmq_exchange, rabbitmq_routing_key,
                           pulsar_thread_count=None, logger=None):
        """
        1. 订阅 pulsar
        2. 处理消费的数据
        3. 将处理后的数据发送到 rabbitmq
        :param task:
        :param pulsar_topic:
        :param pulsar_consumer_name:
        :param rabbitmq_exchange:
        :param rabbitmq_routing_key:
        :param pulsar_thread_count:
        :param logger:
        :return:
        """
        consumer = self.client.create_consumer(pulsar_topic, pulsar_consumer_name)

        def callback(msg):
            result = task(msg)
            if result:
                self.rabbitmq_connect.send([result], rabbitmq_exchange, rabbitmq_routing_key)

        consumer.receive(callback, pulsar_thread_count, logger)

