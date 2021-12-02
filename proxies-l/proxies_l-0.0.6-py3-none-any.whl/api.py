#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 17:30
# @Author  : Adyan
# @File    : index.py


import logging
from flask import Flask, request, g
from flask_cors import CORS
from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from Utils import ReidsClient
from proxy.scheduler import Scheduler


monkey.patch_all()
app = Flask(__name__)

app.config.update(
    DEBUG=True
)
CORS(app, supports_credentials=True)


def get_conn(config):
    if not hasattr(g, 'redis_client'):
        g.redis_client = ReidsClient(
            name=config.get("PROXY_NAME"),
            config={"HOST": config.get("HOST"), "PORT": config.get("PORT"), "DB": config.get("DB"),
                    "PAW": config.get("PASSWORD")}
        )
    return g.redis_client


@app.route('/get', methods=["post", "get"])
def detail():
    key = request.args.to_dict().get("key")
    host = request.args.to_dict().get("HOST")
    port = request.args.to_dict().get("PORT")
    count = request.args.to_dict().get("count")
    ip = request.remote_addr

    s = Scheduler(host, int(port))
    config = s.config
    res = get_conn(config).redis_conn
    logging.info(key)
    if key == "228923910":
        if res.exists(ip):
            res.setrange(ip, 0, int(res.get(ip)) + 1)
        else:
            res.set(ip, 1, ex=3)
        if int(res.get(ip)) < 2:
            # get_conn().put("ssssssss")
            return {
                "code": 200,
                "data": res.srandmember(config.get("PROXY_NAME"), number=count),
                "msg": ""
            }
        else:
            return {
                "code": 111,
                "data": [],
                "msg": "请2秒后再试"
            }
    else:
        return {
            "code": 112,
            "data": [],
            "msg": "密匙错误！！！"
        }


def main(host, port):
    app.run(host=host, port=port)
    http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
