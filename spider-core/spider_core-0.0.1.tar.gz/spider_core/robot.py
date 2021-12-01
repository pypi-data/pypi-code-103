#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from .log import config, log_info


class RobotFactory(object):
    def __init__(self, label):
        self.token = config(label, 'token')
        self.url = config(label, 'url')
        self.number = config(label, "")
        self.headers = {'Content-Type': 'application/json'}

    def send_message(self, content: str, phone: list):
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "mentioned_list": [],
                    "content": content,
                    "mentioned_mobile_list": phone
                }
            }
            _code = 0
            res = requests.post(self.url + self.key, headers=self.headers, data=json.dumps(message), timeout=10)
            if res.status_code == 200:
                return _code
        except Exception as e:
            log_info(e.__str__())
            _code = -1
        return _code

