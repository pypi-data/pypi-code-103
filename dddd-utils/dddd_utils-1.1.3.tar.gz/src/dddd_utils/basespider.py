# -*- coding: utf-8 -*-
"""
爬虫基类
"""
__all__ = [
    'BaseSpider'
]

import redis
import requests
import logging
from dddd_utils.logger import get_logger
from dddd_utils.mysql import StoreMysqlPool
from dddd_utils.mail import UtilMail


class BaseSpider(object):
    def __init__(self, task_name, redis_config=None, mysql_config=None, mail_config=None, log_enabled=True, log_level=logging.DEBUG, log_file_path=None):
        self.use_proxy_request = False  # 是否使用代理
        self.task_name = task_name.lower()

        if log_enabled:
            self.logger = get_logger(name=task_name, log_path=log_file_path, log_level=log_level, log_enabled=log_enabled)

        if redis_config:
            # 连接redis
            conn_pool = redis.ConnectionPool(**redis_config, decode_responses=True)
            self.util_redis = redis.StrictRedis(connection_pool=conn_pool)

        if mysql_config:
            # 连接mysql
            self.util_mysql = StoreMysqlPool(**mysql_config)

        if mail_config:
            # mail
            self.util_mail = UtilMail(**mail_config)

    def send_requests(self, method: str, url: str, headers: dict, params: dict = None, data=None, json=None, proxies: dict = None, verify: bool = False, timeout: int = 10):
        """
        send_requests，可能需要代理，所以简单封装一下
        :param method: 请求方式
        :param url: url
        :param headers: 请求头
        :param params: 作为参数增加到URL中
        :param data: POST时，data其格式必须为字符串
        :param json: POST时，json数据，直接传dict
        :param proxies: 代理，dict
        :param verify: 验证
        :param timeout: 超时
        :return:
        """
        method = method.upper()
        for _ in range(2):
            if self.use_proxy_request:
                proxy_dict = self.get_proxy_ip()
                if proxy_dict.get("username", None) is None:
                    proxies = {
                        "http": f"http://{proxy_dict['ip']}:{proxy_dict['port']}",
                        "https": f"http://{proxy_dict['ip']}:{proxy_dict['port']}"
                    }
                else:
                    proxies = {
                        "http": f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}",
                        "https": f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}"
                    }

            try:
                resp = requests.request(method=method, url=url, headers=headers, params=params, data=data, json=json, proxies=proxies, verify=verify, timeout=timeout)
                return resp
            except Exception as e:
                self.logger.error(e)
        return {"code": 500, "msg": "请求失败"}

    @staticmethod
    def get_proxy_ip():
        """需要重写该方法获取代理ip"""
        return {}
