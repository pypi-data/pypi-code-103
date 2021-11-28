# -*- coding: utf-8 -*-
import pytest
import shutil
import requests
from pathlib import Path

import zwutils.network as network

def test_get_html():
    r = network.get_html('http://www.baidu.com')
    assert r.startswith('<!DOCTYPE html><!--STATUS OK-->')

def test_downfile():
    url = ''
    r = network.downfile(url, settings={'method':'post'},data={'downames': '110000'}, filename='110000')
    assert Path(r).exists()

def test_check_connect():
    r = network.check_connect(['http://www.baidu.com', 'http://123.com'])
    assert r[0][1] == True and r[1][1] == False