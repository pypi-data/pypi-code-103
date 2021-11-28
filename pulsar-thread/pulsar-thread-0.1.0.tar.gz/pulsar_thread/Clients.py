# -*- coding: UTF-8 -*-
# @Time : 2021/11/28 上午12:03 
# @Author : 刘洪波
import pulsar


class Client(object):
    def __init__(self, url: str):
        self.client = pulsar.Client(url)

    def create_consumer(self, topics: list, consumer_name: str, schema=pulsar.schema.StringSchema()):
        from pulsar_thread.Consumers import Consumer
        return Consumer(self.client, topics, consumer_name, schema)

    def create_producer(self):
        from pulsar_thread.Producers import Producer
        return Producer(self.client)

    def close(self):
        self.client.close()
