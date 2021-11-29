# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from flask import Blueprint

from rains.common.api.common import *


task = Blueprint('task', __name__)


@task.route('/task/test', methods=['GET'])
def test():
    return 'test'
