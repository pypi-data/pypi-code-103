#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.common import humanize_bytes, str2pyobj


def test_humanize_bytes():
    assert humanize_bytes(20200) == '19.7 KiB'


def test_str2pyobj():
    x = str2pyobj('{"a":1}')
    assert isinstance(x, dict)

def test_config_read(sample_config):
    assert sample_config['a'] == 1