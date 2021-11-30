#!/usr/bin/env python
from redis import StrictRedis
import json
import time
import sys
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import re
import psutil
import os
import subprocess

import codefast as cf
import requests
cf.logger.logname = '/tmp/vpsstatus.log'
cf.logger.level = 'info'


class Sys:
    @staticmethod
    def call(cmd: str):
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()


class Component(ABC):
    @abstractmethod
    def info(self) -> dict:
        pass


class IP(Component):
    def info(self) -> dict:
        return requests.get('http://ip-api.com/json/').json()


class CPU(Component):
    def info(self) -> float:
        return psutil.cpu_percent(interval=60)


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

    def info(self) -> dict:
        return {'uptime': self.uptime,
                'traffic': self.traffic, 'disk': self.disk}


class Context:
    def __init__(self) -> None:
        sys.path.insert(0, str(Path.home()) + '/.config')
        from redis_sg import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

        self._redis = StrictRedis(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        self._counter = 1
        self._dict = 'vpsstatus'

    @property
    def counter(self) -> int:
        remote_counter = int(self._redis.hget(self._dict, 'counter').decode())
        if remote_counter > self._counter:
            self._counter = remote_counter
        elif remote_counter == self._counter:
            self._counter += 1
        return self._counter

    @property
    def summary(self) -> dict:
        smr = {'ip': IP, 'static': Static,
               'dynamic': Dynamic, 'cpu':CPU}
        return dict((k, V().info()) for k, V in smr.items())

    def run(self):
        ctr = self.counter
        smr = self.summary
        smr['counter'] = ctr
        self._redis.hset(self._dict, 'counter', ctr)
        self._redis.hset(self._dict, smr['static']['name'], json.dumps(smr))
        # cf.info(self._redis.hgetall(self._dict))
        cf.info('update to redis complete')


def entrance():
    while True:
        Context().run()
