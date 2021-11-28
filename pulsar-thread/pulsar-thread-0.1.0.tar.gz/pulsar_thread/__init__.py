# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午5:09 
# @Author : 刘洪波

import pulsar


def client(url: str):
    from pulsar_thread.Clients import Client
    return Client(url)


def create_consumer(clients, topics: list, consumer_name: str, schema=pulsar.schema.StringSchema()):
    from pulsar_thread.Consumers import Consumer
    return Consumer(clients, topics, consumer_name, schema)


def create_producer(clients):
    from pulsar_thread.Producers import Producer
    return Producer(clients)

