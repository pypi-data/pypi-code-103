# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import base64
import hashlib
import hmac
import requests
import socketio
import json
from suanpan.g import g


class API:

    def __init__(self):
        self.config = {"headers": self.defaultHeaders()}
        self.client = None

    def signatureV1(self, secret, data):
        h = hmac.new(secret.encode(), data.encode(), hashlib.sha1)
        return base64.b64encode(h.digest()).decode()

    def defaultHeaders(self):
        return {
            g.userIdHeaderField:
                g.userId,
            g.userSignatureHeaderField:
                self.signatureV1(g.accessSecret, g.userId),
            g.userSignVersionHeaderField:
                "v1",
        }

    def sioClient(self, *args, **kwargs):
        kwargs["headers"] = {
            **self.defaultHeaders(),
            **kwargs.pop("headers", {})
        }
        self.client = socketio.Client()
        self.client.connect(*args, **kwargs)

    def get(self, url):
        content = requests.get(url, **self.config).content
        try:
            return json.loads(content)
        except:
            return content

    def post(self, url, **kwds):
        self.config.update(kwds)
        content = requests.get(url, **self.config).content
        try:
            return json.loads(content)
        except:
            return content

    def getUrl(self, path):
        protocol = "https" if g.hostTls else "http"
        host = f"{g.host}:{g.port}" if g.os == "windows" else g.host
        return f"{protocol}://{host}{path}"

    def getOssToken(self):
        return self.get(self.getUrl("/oss/token"))
