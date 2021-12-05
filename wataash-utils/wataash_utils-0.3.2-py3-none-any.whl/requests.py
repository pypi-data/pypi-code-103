# SPDX-License-Identifier: Apache-2.0

import json
import typing as t

from wataash_utils.json import JSON
from wataash_utils.logging import logger
from wataash_utils.str import partial_str
import requests


def _debug_json_partially(jsn: JSON):
    logger.debug(partial_str(json.dumps(jsn, ensure_ascii=False), 50))


def _raise_for_status(resp: requests.Response, url: str, method: str):
    if 400 <= resp.status_code < 500 or 500 <= resp.status_code < 600:
        logger.error(f'{method} {url}: received {resp.status_code}')
        logger.error(f'resp.text: {resp.text}')
        resp.raise_for_status()


def json_get(*, url: str, params=None, allow_404=False, **kwargs) \
        -> t.Optional[JSON]:
    """
    :return: None on allow_404 && 404
    """

    logger.debug(f'GET {url}')
    resp = requests.get(url, params, **kwargs)
    if allow_404 and resp.status_code == 404:
        logger.debug(f'404: {resp.text}')
        return None
    _raise_for_status(resp, url, 'GET')
    logger.debug(f'{resp.status_code} {resp.reason}')
    r_json = resp.json()
    _debug_json_partially(r_json)
    return r_json


def json_post(*, url: str, json: JSON, **kwargs) -> JSON:
    logger.debug(f'POST {url} {partial_str(str(json))}')
    resp = requests.post(url, json=json, **kwargs)
    _raise_for_status(resp, url, 'POST')
    logger.debug(f'{resp.status_code} {resp.reason}')
    r_json = resp.json()
    _debug_json_partially(r_json)
    return r_json


def json_patch(*, url: str, json: JSON, **kwargs) -> JSON:
    logger.debug(f'PATCH {url} {partial_str(str(json))}')
    resp = requests.patch(url, json=json, **kwargs)
    _raise_for_status(resp, url, 'PATCH')
    logger.debug(f'{resp.status_code} {resp.reason}')
    r_json = resp.json()
    _debug_json_partially(r_json)
    return r_json


def json_delete(*, url: str, json: JSON, **kwargs) -> JSON:
    logger.debug(f'DELETE {url} {partial_str(str(json))}')
    resp = requests.delete(url, json=json, **kwargs)
    _raise_for_status(resp, url, 'DELETE')
    logger.debug(f'{resp.status_code} {resp.reason}')
    r_json = resp.json()
    _debug_json_partially(r_json)
    return r_json
