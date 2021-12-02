#!/usr/bin/env python
from redis import StrictRedis
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import re
import psutil
import os
import subprocess, arrow

import codefast as cf
import requests
import asyncio


class Sys:
    @staticmethod
    def call(cmd: str) -> str:
        try:
            return subprocess.check_output(cmd,
                                           shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            return ''


class Component(ABC):
    @abstractmethod
    def info(self) -> dict:
        pass


class IP(Component):
    IPINFO = None

    def info(self) -> dict:
        if IP.IPINFO is None:
            IP.IPINFO = requests.get('http://ip-api.com/json/').json()
        return IP.IPINFO


class CPU(Component):
    SAVED_DATA = []

    def __init__(self, iterval: int = 3) -> None:
        self.iterval = iterval

    def info(self) -> float:
        return psutil.cpu_percent(interval=self.iterval)


class Static(Component):
    def __init__(self, config_path: str = 'vpsstatus.json') -> None:
        self.config_path = config_path

    def info(self) -> dict:
        return cf.js(os.path.join(Path.home(), '.config', self.config_path))


class Dynamic(Component):
    @property
    def uptime(self) -> str:
        uptime = Sys.call('uptime')
        return re.search(r'up (.*?),', uptime).group(1)

    @property
    def traffic(self) -> dict:
        return json.loads(Sys.call('vnstat --json d'))

    @property
    def disk(self) -> dict:
        total, used, free = shutil.disk_usage("/")
        return {'total': total, 'used': used, 'free': free}

    @property
    def last_active(self) -> str:
        return arrow.now().format('YYYY-MM-DD HH:mm:ss')

    def info(self) -> dict:
        return {
            'uptime': self.uptime,
            'traffic': self.traffic,
            'disk': self.disk,
            'last_active': self.last_active
        }


class Context:
    def __init__(self) -> None:
        sys.path.insert(0, str(Path.home()) + '/.config')
        from redis_sg import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

        self._redis = StrictRedis(host=REDIS_HOST,
                                  port=REDIS_PORT,
                                  password=REDIS_PASSWORD)
        self._counter = 1
        self._dict = 'vpsstatus'
        self.init_redis()

    def init_redis(self):
        if self._redis.hget(self._dict, b'counter') is None:
            self._redis.hset(self._dict, b'counter', 42)

    @property
    def counter(self) -> int:
        remote_counter = int(self._redis.hget(self._dict, 'counter').decode())
        if remote_counter > self._counter:
            self._counter = remote_counter
        self._counter += 1
        return self._counter

    @property
    def summary(self) -> dict:
        smr = {'ip': IP, 'static': Static, 'dynamic': Dynamic, 'cpu': CPU}
        return dict((k, V().info()) for k, V in smr.items())

    def run(self):
        ctr = self.counter
        smr = self.summary
        smr['counter'] = ctr
        self._redis.hset(self._dict, 'counter', ctr)
        self._redis.hset(self._dict, smr['static']['name'], json.dumps(smr))
        # cf.info(self._redis.hgetall(self._dict))
        cf.info('update to redis complete')


async def cpu_usage(window: int = 600):
    n_float = 0
    for _ in range(window):
        n_float += psutil.cpu_percent(interval=None)
        await asyncio.sleep(1)
    n_float /= window
    CPU.SAVED_DATA.append(n_float)
    return n_float


async def main():
    while True:
        Context().run()
        # asyncio.create_task(cpu_usage(10))
        await asyncio.sleep(0.1)


def entrance():
    asyncio.run(main())
