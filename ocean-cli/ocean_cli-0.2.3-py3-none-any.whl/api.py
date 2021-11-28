from json.decoder import JSONDecodeError
import requests
import json
import traceback
import sys
import urllib3
from urllib.parse import urljoin

from ocean import code, utils
from ocean.utils import sprint, PrintType


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def init(ctx, path, headers):
    url = urljoin(ctx.get_url(), path)

    h = {"Content-Type": "application/json", "Accept": "application/json"}
    h.update(headers)
    if ctx.get_token():
        h.update({"Authorization": "Bearer " + ctx.get_token()})

    return url, h


def handler(res):
    if res.status_code // 100 == 2:
        return res
    elif res.status_code == 401:
        sprint("Authentication Failed. ", PrintType.FAILED)
        sprint("Please run:\n\n\tocean login\n")
        exit()
    elif res.status_code == 404:
        sprint(f"[{res.status_code}] Request Failed. ", PrintType.FAILED)
        exit()
    else:
        try:
            body = res.json()
            if isinstance(body, dict):
                message = body.get("message")
                detail = body.get("detail")
                sprint(f"[{res.status_code}] {message} {detail}", PrintType.FAILED)
                exit()
            elif isinstance(body, list):
                for item in body:
                    message = item.get("message")
                    detail = body.get("detail")
                    sprint(f"[{res.status_code}] {message} {detail}", PrintType.FAILED)
                exit()
        except JSONDecodeError:
            sprint(f"[{res.status_code}] {res.text}", PrintType.FAILED)
            exit()


def _request(method, ctx, path, data=None, headers={}, timeout=10, **kwargs):
    url, h = init(ctx, path, headers)
    try:
        res = method(url, data=json.dumps(data), headers=h, timeout=timeout, **kwargs)
        return handler(res)
    except requests.exceptions.Timeout:
        sprint("Request Timeout.", PrintType.FAILED)
        exit()
    except Exception:
        sprint(f"Request Failed.", PrintType.FAILED)
        traceback.print_exc(file=sys.stdout)
        exit()


def get(ctx, path, headers={}, **kwargs):
    return _request(requests.get, ctx, path, headers=headers, **kwargs)


def post(ctx, path, data=None, headers={}, **kwargs):
    return _request(requests.post, ctx, path, data=data, headers=headers, **kwargs)


def delete(ctx, path, data=None, headers={}, **kwargs):
    return _request(requests.delete, ctx, path, data=data, headers=headers, **kwargs)


def get_id_from_machine_type(ctx, type_name):
    res = get(ctx, "/api/users/resources")
    body = utils.dict_to_namespace(res.json())

    for mt in body.machineTypes:
        if mt.name == type_name:
            return mt.id

    return None


def get_volume_id_from_volume_name(ctx, volume_name):
    res = get(ctx, "/api/volumes")
    body = utils.dict_to_namespace(res.json())

    for vol in body.volumes:
        if vol.name == volume_name:
            return vol.volumeName

    return None
