#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/6 10:32
# @Author  : Adyan
# @File    : index.py


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 17:30
# @Author  : Adyan
# @File    : index.py
import logging
import random
import subprocess
import json
import re
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from .cookies import Cookies
from ..config_mongo import settings

monkey.patch_all()
app = Flask(__name__)

app.config.update(
    DEBUG=True
)
CORS(app, supports_credentials=True)
set = settings.Settings


# TB_detail
@app.route('/cookie', methods=["post", "get"])
def detail():
    types = request.args.to_dict().get("type")
    host = request.args.to_dict().get("host")
    config = set(host=host).config
    print(config)
    if types:
        # time.sleep(random.randint(20, 120))
        return Cookies().taobao_cookies(config.get(types))
    return "None"


def start(host, prot):
    """9090"""
    app.run(host=host, port=prot)
    http_server = WSGIServer((host, prot), app, handler_class=WebSocketHandler)
    http_server.serve_forever()

