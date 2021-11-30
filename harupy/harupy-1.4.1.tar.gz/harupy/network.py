#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


def get_external_ip():
    try:
        return requests.get('https://checkip.amazonaws.com').text.strip()
    except:
        return None
