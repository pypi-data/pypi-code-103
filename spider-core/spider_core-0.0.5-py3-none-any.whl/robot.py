#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from .log import config, log_info


class RobotFactory(object):
    def __init__(self, label):
        self.token = config(label, 'token')
        self.url = config(label, 'url')
        self.number = config(label, "number")
        self.headers = {'Content-Type': 'application/json'}

    def send_message(self, content: str):
        try:
            message = {
                "content": content,
                "notifyParams": [{
                    "type": "jobNos",
                    "values": self.number.split(",")
                }]
            }
            _code = 0
            res = requests.post(self.url + self.token, headers=self.headers, data=json.dumps(message), timeout=10)
            if res.status_code == 200:
                return _code
        except Exception as e:
            log_info(e.__str__())
            _code = -1
        return _code

