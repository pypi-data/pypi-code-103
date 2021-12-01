#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 17:30
# @Author  : Adyan
# @File    : scheduler.py
import hashlib
import time
from multiprocessing import Process
import aiohttp
import asyncio
from Utils import ProxyGetter, ReidsClient
from proxies.proxy.proxy.settings import *

proxy = PROXY_API.get(PROXY_OFF)


class VaildityTester(object):
    """
    校验器
    """

    def __init__(self):
        self.__raw_proxies = []
        self.md5 = hashlib.md5()

    def set_raw_proxies(self, proxiies):
        self.__raw_proxies = proxiies
        # 数据库连接-->创建的方式会影响程序性能--》用的时候创建
        self.__conn = ReidsClient(
            name=PROXY_NAME,
            config={"HOST": HOST, "PORT": PORT, "DB": DB}
        )

    async def test_single_proxy(self, proxy):
        """
        校验单一代理
        :param proxy:
        :return:
        """
        try:
            async with aiohttp.ClientSession() as session:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = proxy.replace("s", "")
                try:
                    async with session.get(
                            TSET_API,
                            headers=TEST_HEADERS,
                            proxy=real_proxy,
                            timeout=TEST_TIME_OUT
                    ) as response:
                        if response.status == 200:
                            try:
                                self.__conn.sput(proxy)
                            except:
                                pass
                except Exception as e:
                    print('代理不可用！', proxy, e)
        except Exception:
            print('未知错误！')

    def tester(self):
        """
        使用校验器的步骤：
            1、先往篮子放ip
            self.set_raw_proxies(proxies)
            2、启动校验器
            self.tester()
        校验器的开关
        :return:
        """
        # 1、创建任务循环loop
        loop = asyncio.get_event_loop()
        # 2、启动校验代理功能
        tasks = [self.test_single_proxy(proxy) for proxy in self.__raw_proxies]
        # 3、监听tasks是否创建
        loop.run_until_complete(asyncio.wait(tasks))


class PoolAdder(object):
    def __init__(self, threshold):
        self.__threshold = threshold
        # 校验
        self.__tester = VaildityTester()
        # db
        self.__conn = ReidsClient(
            name=PROXY_NAME,
            config={"HOST": HOST, "PORT": PORT, "DB": DB}
        )
        # getter
        self.__getter = ProxyGetter(
            proxy.get('url'),
            proxy.get('name'),
            add_whitelist=proxy.get('add_whitelist'),
            del_whitelist=proxy.get('del_whitelist')
        )

    def is_over_threshold(self):
        """
        判断代理池中代理的数量是否到达最大值
        :return:True:超过
        """
        if self.__conn.queue_len >= self.__threshold:
            return True
        return False

    def add_to_pool(self):
        while True:
            # 代理池超出最大代理数量就停止添加
            if self.is_over_threshold():
                break
            proxy_count = 0
            '__crawl_func__'

            try:
                proxies = self.__getter.get_proxies()
                if proxies:
                    proxy_count += len(proxies)
            except Exception as e:
                print('代理网站发生异常，请查看变更！', e)
                continue

                # print(proxies)
                # 2、使用校验器校验
                # 放材料

            if proxies:
                print(proxies)
                self.__tester.set_raw_proxies(proxies)
                self.__tester.tester()
                if proxy_count == 0:
                    raise RuntimeError('所有的代理网站都不可用，请变更！')


class Scheduler(object):

    # 1、循环校验--->不断的从代理池头部获取中一片，做定期检查
    @staticmethod
    def vaild_proxy(cycle=CYCLE_VAILD_TIME):
        conn = ReidsClient(
            name=PROXY_NAME,
            config={"HOST": HOST, "PORT": PORT, "DB": DB}
        )
        tester = VaildityTester()

        # 循环校验
        while True:
            count = int(conn.queue_len * 0.5)
            if count == 0:
                time.sleep(CYCLE_VAILD_TIME)
                count = int(conn.queue_len * 0.5)
            proxies = conn.redis_conn.spop(PROXY_NAME, count)
            # 校验
            tester.set_raw_proxies(proxies)
            tester.tester()
            time.sleep(CYCLE_VAILD_TIME)

    @staticmethod
    def check_pool_add(
            lower_threshold=LOWER_THRESHOLD,
            upper_threshold=UPPER_THRESHOLD,
            cycle=ADD_CYCLE_TIME
    ):
        adder = PoolAdder(upper_threshold)
        conn = ReidsClient(
            name=PROXY_NAME,
            config={"HOST": HOST, "PORT": PORT, "DB": DB}
        )
        while True:
            if conn.queue_len <= lower_threshold:
                adder.add_to_pool()
            time.sleep(cycle)

    def run(self):
        p1 = Process(target=Scheduler.vaild_proxy)  # 校验器
        p2 = Process(target=Scheduler.check_pool_add)  # 添加器
        p1.start()
        p2.start()


# if __name__ == '__main__':
#     res = ReidsClient(
#         name=PROXY_NAME,
#         config={"HOST": HOST, "PORT": PORT, "DB": DB}
#     )
#     # print(res.redis_conn.spop(PROXY_NAME, count=3))
#     for i in ['https://36.57.68.124:4332', 'https://182.107.232.116:4331', 'https://27.190.75.165:4341',
#               'https://27.159.184.58:43681', 'https://221.10.104.146:43311', 'https://60.185.34.176:43451']:
#         res.sput(i)
#
#     Scheduler().vaild_proxy()
#     print(ReidsClient(
#         name=PROXY_NAME,
#         config={"HOST": HOST, "PORT": PORT, "DB": DB}
#     ).redis_conn.spop())
# adder = PoolAdder(100)
# adder.add_to_pool()
