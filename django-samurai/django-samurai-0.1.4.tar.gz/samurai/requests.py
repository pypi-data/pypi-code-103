#!/usr/bin/env python3

from urllib import request
import json


# HTTP verbs


def post(url, json_data, custom_headers=None):
    req = request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    if custom_headers:
        for cn, cv in custom_headers.items():
            req.add_header(cn, cv)
    return request.urlopen(req, data=json.dumps(json_data).encode())


def get(url, custom_headers=None):
    req = request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    if custom_headers:
        for cn, cv in custom_headers.items():
            req.add_header(cn, cv)
    return request.urlopen(req)
