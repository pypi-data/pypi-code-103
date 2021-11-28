# -*- coding: UTF-8 -*-
# @Time : 2021/11/27 下午6:15 
# @Author : 刘洪波
import pulsar
from concurrent.futures import ThreadPoolExecutor


class Producer(object):
    def __init__(self, client):
        self.client = client

    def send(self, msg_dict, thread_count=5, schema=pulsar.schema.StringSchema()):
        pool = ThreadPoolExecutor(max_workers=thread_count)
        for topic, contents in msg_dict.items():
            producer = self.client.create_producer(topic, schema=schema)

            def send_msg(cs, p):
                for content in cs:
                    p.send(content)
                p.close()
            pool.submit(send_msg, contents, producer)
        return True

    def send_async(self, msg_dict, thread_count=5, callback=None, schema=pulsar.schema.StringSchema()):
        pool = ThreadPoolExecutor(max_workers=thread_count)
        for topic, contents in msg_dict.items():
            producer = self.client.create_producer(topic, schema=schema)

            def send_msg(cs, p, cb):
                for content in cs:
                    p.send_async(content, callback=cb)
                p.close()
            pool.submit(send_msg, contents, producer, callback)
        return True
