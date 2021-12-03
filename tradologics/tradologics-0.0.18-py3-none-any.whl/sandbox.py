#!/usr/bin/env python3
# -*-encoding: utf-8-*-

import json
import requests


_SANDBOX_URL = "https://api.tradologics.com/v1/sandbox"
_TOKEN = None


def set_token(token):
	global _TOKEN
	_TOKEN = token


def tradehook(kind, strategy=None, **kwargs):
	"""
	authorization required

	Parameters
	----------
	kind : available kinds: ["bar", "order", "order_{YOUR_STATUS}  (example: "order_filled")", "position",
	"position_expire", "price", "price_expire", "error"]
	strategy : callback
	kwargs : payload

	Returns
	-------
	json obj
	"""

	url = f'{_SANDBOX_URL}/{kind.replace("_", "/")}'
	headers = {'Authorization': _TOKEN}
	result = requests.get(url, data=json.dumps(kwargs), headers=headers)
	strategy(kind.split('_')[0], result.json())
