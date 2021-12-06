import json

from hashlib import sha1
from functools import reduce
from base64 import b85decode, b64decode


def generate_device_info():
    try:
        deviceId = "22C238D43575D538070F4D9794CFA2968235D18929869E747B17A5F2735EC6E2E74F5962662B8A861C"
    except Exception:
        deviceId = "227D08450A6191A2B3372A55FCBB4D65D9ED996B4C2FB04E01560D88016CA1354151522FEA9081E8D3"

    return {
        "device_id": deviceId,
        "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
    }

# okok says: please use return annotations :(( https://www.python.org/dev/peps/pep-3107/#return-values

def decode_sid(sid: str) -> dict:
    return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]
