#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 17:30
# @Author  : Adyan
# @File    : scheduler.py
import hashlib
import logging
import time
import threading
from datetime import datetime
from multiprocessing import Process
import aiohttp
import asyncio
from Utils import ProxyGetter, ReidsClient, Headers, MongoPerson


class Settings:
    def __init__(self, host, port):
        self.config = MongoPerson(
            'config', 'proxy',
            config={"host": host, "port": port}
        ).find_one()


class VaildityTester(object):
    """
    校验器
    """

    def __init__(self, config):
        self.__raw_proxies = []
        self.md5 = hashlib.md5()
        self.config = config

    def set_raw_proxies(self, proxiies):
        self.__raw_proxies = proxiies
        # 数据库连接-->创建的方式会影响程序性能--》用的时候创建
        self.__conn = ReidsClient(
            name=self.config.get("PROXY_NAME"),
            config={
                "HOST": self.config.get("HOST"),
                "PORT": self.config.get("PORT"),
                "DB": self.config.get("DB"),
                "PAW": self.config.get("PASSWORD")
            })

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
                            self.config.get("TSET_API"),
                            headers=Headers().headers(),
                            proxy=real_proxy,
                            timeout=self.config.get("TEST_TIME_OUT")
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
    # s = Settings('H', 'H')
    def __init__(self, threshold, config):
        self.__threshold = threshold
        # self.s = Settings('H','H')
        proxy = config.get("PROXY_API").get(config.get('PROXY_OFF'))
        # 校验
        self.__tester = VaildityTester(config)
        # db
        self.__conn = ReidsClient(
            name=config.get("PROXY_NAME"),
            config={"HOST": config.get("HOST"), "PORT": config.get("PORT"), "DB": config.get("DB"),
                    "PAW": config.get("PASSWORD")}
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
                if isinstance(proxies, list):
                    proxy_count += len(proxies)
                else:
                    logging.info(f'{proxies}代理网站发生异常，请查看变更！')
                    print(f'{proxies}代理网站发生异常，请查看变更！')
            except Exception as e:
                logging.info(f'代理网站发生异常，请查看变更！{e}')
                continue

                # print(proxies)
                # 2、使用校验器校验
                # 放材料
            if proxies and "试" not in proxies:
                self.__tester.set_raw_proxies(proxies)
                self.__tester.tester()
                if proxy_count == 0:
                    raise RuntimeError('所有的代理网站都不可用，请变更！')


class Scheduler(object):

    def __init__(self, host=None, port=None):
        if host:
            s = Settings(host, port).config
            s.pop("_id")
            self.config = s

    # 1、循环校验--->不断的从代理池头部获取中一片，做定期检查
    @staticmethod
    def vaild_proxy(config):
        conn = ReidsClient(
            name=config.get("PROXY_NAME"),
            config={"HOST": config.get("HOST"), "PORT": config.get("PORT"), "DB": config.get("DB"),
                    "PAW": config.get("PASSWORD")}
        )
        tester = VaildityTester(config)

        # 循环校验
        retry = 0
        while True:
            count = int(conn.queue_len * 0.5)
            if retry == 120:
                logging.info(f'redis ip 当前存量：{count} 重试次数：{retry}，请检测ip添加')
                print(f'redis ip 当前存量：{count} 重试次数：{retry}，请检测ip添加')
                break
            if count == 0:
                retry += 1
                time.sleep(config.get("CYCLE_VAILD_TIME"))
                count = int(conn.queue_len * 0.5)
            proxies = conn.redis_conn.spop(config.get("PROXY_NAME"), count)
            if proxies:
                retry -= 1
                # 校验
                tester.set_raw_proxies(proxies)
                tester.tester()
                time.sleep(config.get("CYCLE_VAILD_TIME"))

    @staticmethod
    def check_pool_add(config):
        lower_threshold = config.get("LOWER_THRESHOLD")
        upper_threshold = config.get("UPPER_THRESHOLD")
        cycle = config.get("ADD_CYCLE_TIME")
        adder = PoolAdder(upper_threshold, config=config)
        conn = ReidsClient(
            name=config.get("PROXY_NAME"),
            config={"HOST": config.get("HOST"), "PORT": config.get("PORT"), "DB": config.get("DB"),
                    "PAW": config.get("PASSWORD")}
        )
        while True:
            if datetime.now().hour in [1, 2, 3, 4, 5, 6, 20, 21, 22, 23, 0]:
                print(datetime.now().hour)
                time.sleep(cycle)
            else:
                count = conn.queue_len
                if count <= lower_threshold:
                    logging.info(f'获取代理，当前代理数量{count}')
                    print(f'获取代理，当前代理数量{count}')
                    adder.add_to_pool()
            time.sleep(cycle)

    def run(self, config):
        S = Scheduler()
        p1 = Process(target=S.vaild_proxy, args=(config,))  # 校验器
        p2 = Process(target=S.check_pool_add, args=(config,))  # 添加器
        p1.start()
        p2.start()
