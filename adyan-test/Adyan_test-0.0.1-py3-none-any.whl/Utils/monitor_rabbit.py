#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/2 13:34
# @Author  : Adyan
# @File    : monitor_rabbit.py
import json
import time
import traceback
import logging

from pika.exceptions import ConnectionClosedByBroker, AMQPChannelError, AMQPConnectionError


class MonitorRabbit:
    def __init__(
            self, rabbit_conn, redis_coon,
            redis_key=None, callback=None
    ):
        """
        :param rabbit_conn: rabbit链接
        :param redis_coon: redis链接
        :param redis_key: redis储存的键
        :param callback: 方法
        """
        self.rabbit_conn = rabbit_conn
        self.redis_coon = redis_coon
        self.redis_key = redis_key
        self._callback = callback

    def start_run(self):
        """
        监听队列
        :return:
        """
        while True:
            try:
                self.rabbit_conn.get_rabbit(self.callback)
            except ConnectionClosedByBroker:
                logging.info(f'error  [{ConnectionClosedByBroker}]')
                time.sleep(10)
                continue
            except AMQPChannelError:
                logging.info(f'error  [{AMQPChannelError}]')
                time.sleep(10)
                continue
            except AMQPConnectionError:
                # traceback.print_exc()
                logging.info(f'error  [{AMQPConnectionError}]')
                time.sleep(10)
                continue
            except:
                traceback.print_exc()
                logging.info(f'error  [{"unknow error"}]')
                time.sleep(10)
                continue

    def callback(self, channel, method, properties, body):
        """
        回调函数
        """
        try:
            req_body = body.decode('utf-8')
            logging.info(req_body)
            mes = {'result': json.loads(req_body)}
            if self._callback:
                self._callback.shop_start(json.dumps(mes))
            else:
                self.redis_coon.lpush(f'{self.redis_key}:start_urls', json.dumps(mes, ensure_ascii=False))
        except Exception as e:
            print(e)
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)
