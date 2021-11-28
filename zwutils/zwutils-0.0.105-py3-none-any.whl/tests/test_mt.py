# -*- coding: utf-8 -*-
import pytest
import shutil
import requests
from pathlib import Path

from zwutils.mthreading import multithread_task
from zwutils.network import multithread_request
from zwutils import fileutils

class TestMP:
    def test_mtask(self):
        num = 100
        shutil.rmtree('data', ignore_errors=True)
        args = [{'path':'data/p%s.txt'%i, 'txt':i} for i in range(num)]
        multithread_task(fileutils.writefile, args)
        count = len( list(Path('data').glob('*.txt')) )
        shutil.rmtree('data', ignore_errors=True)
        assert count == num

    def test_mrequest(self):
        num = 3
        urls = ['http://httpbin.org/get' for i in range(num)]
        rtn = multithread_request(urls, params_list=[{'key':'yew', 'value':i} for i in range(num)])
        assert len(rtn) == num

    def test_mrequest_post(self):
        num = 3
        urls = ['http://httpbin.org/post' for i in range(num)]
        def gen_proxy():
            r = requests.get('http://66.98.114.234:13603/proxy/get')
            return r.json()
        settings = {
            'method': 'post',
            'proxies': gen_proxy,
        }
        rtn = multithread_request(urls, settings, json_list=[{'key':'yew', 'value':i} for i in range(num)], verify=False)
        assert len(rtn) == num