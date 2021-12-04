import json

import requests

from rainiee_lib.lib.utils import *



class FeishuClient(object):
    def __init__(self):
        info('feishu client init')
        self.headers = {'Content-Type': 'application/json'}

    def send(self,message,url):
        req_json = {
            "msg_type":"text",
            "content":{"text":message}
        }
        res = requests.post(url,json = req_json ,headers=self.headers)
        info(res.text)

    def mass(self,message,urls):
        for url in urls:
            self.send(message,url)