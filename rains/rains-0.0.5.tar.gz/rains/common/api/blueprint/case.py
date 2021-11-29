# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from flask import Blueprint

from rains.common.api.common import *


case = Blueprint('case', __name__)


@case.route('/case/test', methods=['GET'])
def test():
    return 'test'
