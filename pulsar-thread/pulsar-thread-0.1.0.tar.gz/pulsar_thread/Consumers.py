# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午5:36 
# @Author : 刘洪波

from concurrent.futures import ThreadPoolExecutor


class Consumer(object):
    def __init__(self, client, topics, consumer_name, schema):
        self.consumer = client.subscribe(topics, consumer_name, schema=schema)

    def receive(self, task, timeout_millis=None, logger=None):
        """
        消费一个，处理一个
        :param task: 任务程序
        :param timeout_millis: 订阅超时限制(慎用)
        :param logger: 日志收集器
        :return:
        """
        while True:
            msg = self.consumer.receive(timeout_millis)
            self.acknowledge(task, msg, logger)

    def receive_thread(self, task, thread_count=5, timeout_millis=None, logger=None):
        """
        多线程处理
        :param task: 任务程序
        :param thread_count: 指定最大线程数
        :param timeout_millis: 订阅超时限制 (慎用)
        :param logger: 日志收集器
        :return:
        """
        pool = ThreadPoolExecutor(max_workers=thread_count)
        while True:
            msg = self.consumer.receive(timeout_millis)
            pool.submit(self.acknowledge, task, msg, logger)

    def acknowledge(self, task, msg, logger):
        try:
            task(msg)
            self.consumer.acknowledge(msg)
        except Exception as e:
            # 消息未被成功处理
            self.consumer.negative_acknowledge(msg)
            if logger:
                logger.error(e)
