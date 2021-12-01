#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: similraface
# @contact: yangwubing@molbreeding.com
# @software: PyCharm
# @file: base.py
# @time: 2021/12/1 11:41 上午
# @desc:
import os
import uuid
import subprocess
import requests
import json


def generator_uuid_dir(base_dir='/tmp', makedirs=True):
    uid = uuid.uuid4().hex
    lpath = os.path.join(base_dir, uid)
    if makedirs:
        os.makedirs(lpath)
    return lpath


def generator_output_dir(outer_name):
    p_dir = generator_uuid_dir()
    return os.path.join(p_dir, outer_name)


def generator_tmp_file(outer_name=None, base_dir='/tmp'):
    p_dir = generator_uuid_dir(base_dir=base_dir)
    if outer_name is None:
        outer_name = uuid.uuid4().hex
    return os.path.join(p_dir, outer_name)


def generator_cmd(tool_bin, parameters: list = []):
    cmd = tool_bin
    for itor in parameters:
        cmd = f"{cmd} {itor[0]} {itor[1]}"
    return cmd


def cmd_run(cmd):
    flag = subprocess.check_call(cmd=cmd, shell=True)
    return flag


def report(url, post_data):
    re = requests.put(url, json.dumps(post_data))
    return re
