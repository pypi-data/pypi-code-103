# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from flask import Blueprint

from rains.common.api.common import *


data = Blueprint('data', __name__)


@data.route('/data/test', methods=['GET'])
def test():
    return 'test'
