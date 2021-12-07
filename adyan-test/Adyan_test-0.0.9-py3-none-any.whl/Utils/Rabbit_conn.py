#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 14:46
# @Author  : Adyan
# @File    : Rabbit_conn.py


import json
import pika


class RabbitClient:
    def __init__(self, queue_name, config):
        """
        :param queue_name:
        :param config: {
            "mq_ip": "ip",
            "mq_port": 30002,
            "mq_virtual_host": "my_vhost",
            "mq_username": "dev",
            "mq_pwd": "zl123456",
            "prefix": ""
            }
        """
        self.queue_name = queue_name
        self.config = config

    def rabbit_conn(self):
        """
        创建连接
        :return:
        """
        user_pwd = pika.PlainCredentials(
            self.config.get("mq_username"),
            self.config.get("mq_pwd")
        )
        params = pika.ConnectionParameters(
            host=self.config.get("mq_ip"),
            port=self.config.get('mq_port'),
            virtual_host=self.config.get("mq_virtual_host"),
            credentials=user_pwd
        )
        self.conn = pika.BlockingConnection(parameters=params)
        self.col = self.conn.channel()
        self.col.queue_declare(
            queue=self.queue_name,
            durable=True
        )

    def push_rabbit(self, item):
        self.rabbit_conn()
        self.col.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(item, ensure_ascii=False)
        )

    def get_rabbit(self, fun):
        self.rabbit_conn()
        self.col.queue_declare(self.queue_name, durable=True, passive=True)
        self.col.basic_consume(self.queue_name, fun)
        self.col.start_consuming()
