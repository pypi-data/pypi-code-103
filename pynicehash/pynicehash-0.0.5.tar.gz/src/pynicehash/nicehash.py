import datetime
import uuid
from time import mktime
from enum import Enum
import json
import hashlib
import hmac
import requests
import logging

from pynicehash.miningrig import MiningRig

class MiningStatus(Enum):
    START = "START"
    STOP = "STOP"
    POWER_MODE = "POWER_MODE"


class NiceHash(object):
    def __init__(self, api_url, organisation_id, api_key, api_secret):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.organisation_id = organisation_id

    def get_epoch_ms_from_now(self):
        now = datetime.datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def generate_headers(self, method, path, query = "", data = None):
        x_time = self.get_epoch_ms_from_now()
        x_nonce = str(uuid.uuid4())

        message = bytearray(self.api_key, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(str(x_time), 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(x_nonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(method, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(path, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(query, 'utf-8')

        if data is not None:
            body_json = json.dumps(data)
            message += bytearray('\x00', 'utf-8')
            message += bytearray(body_json, 'utf-8')

        digest = hmac.new(bytearray(self.api_secret, 'utf-8'), message, hashlib.sha256).hexdigest()
        xauth = self.api_key + ":" + digest

        return {
            "X-Time": str(x_time),
            "X-Nonce": x_nonce,
            "X-Organization-Id": self.organisation_id,
            "X-Request-Id": str(uuid.uuid4()),
            "X-Auth": self.api_key + ":" + digest,  
            "X-User-Agent": "py-nicehash",
            "X-User-Lang": "en"
            }

    def get(self, path, query = ""):
        url = self.api_url + path

        logging.getLogger(__name__).debug(f"GET REQUEST:{url}?{query}")

        response = requests.get(url, headers = self.generate_headers("GET", path, query))
        if response.status_code != 200:
            if response.status_code == 500:
                msg = []
                for e in response.json().errors:
                    msg.append(f"{e.code}: {e.message}")
                raise Exception(", ".join(msg))
            else:
                raise Exception(f"{response.status_code}: {response.reason} {url}")

        logging.getLogger(__name__).debug(f"GET RESPONSE:{url} - {response.content}")

        return response.json()

    def post(self, path, query = "", data = None):
        url = self.api_url + path

        logging.getLogger(__name__).debug(f"POST REQUEST:{url}?{query} {data}")

        response = requests.post(url, headers = self.generate_headers("POST", path, query, data), json = data)
        if response.status_code != 200:
            if response.status_code == 500:
                msg = []
                for e in response.json().errors:
                    msg.append(f"{e.code}: {e.message}")
                raise Exception(", ".join(msg))
            else:
                raise Exception(f"{response.status_code}: {response.reason} {url}")

        logging.getLogger(__name__).debug(f"POST RESPONSE:{url} - {response.content}")
        
        return response.json()

    def get_rigs(self):
        response = self.get("/main/api/v2/mining/rigs2")
        return_value = []
        for r in response["miningRigs"]:
            return_value.append(MiningRig(self, r))
        return return_value

    def get_rig_detail(self, rig_id):
        return self.get(f"/main/api/v2/mining/rig2/{rig_id}")

    def set_device_status(self, device, mining_status):
        return self.post(f"/main/api/v2/mining/rigs/status2", data = {
            "rigId": device.parent_rig.id,
            "deviceId": device.id,
            "action": mining_status.value
            })


