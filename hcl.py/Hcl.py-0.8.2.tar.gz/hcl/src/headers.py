import hmac
import base64
import json
from hashlib import sha1
from uuid import uuid4

# ========= .HEADERS DEFINITIONS ===========
deviceId = None
userId = None
sid = None


# =============== HEADERS ================
class Headers:
    def __init__(self, data = None, type: str = None):
        self.deviceId = deviceId
        self.userId = userId
        self.sid = sid
        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 9.0.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33587"
        self.headers = {
            "NDCLANG": "en",
            "NDCDEVICEID": self.deviceId,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        self.web_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "cookie": "auc=e72277dd1793efef0c5ba0db4d8; qca=P0-2125635587-1620259566756; G_ENABLED_IDPS=google; gads=ID=fd25c8819b58298c:T=1620259596:S=ALNI_MYgGClDj--AgWtT6Oa_pvn5ENBUcw; gdpr_cookie_agreee=1; exp=60-0; asc=; _ga_9SJ4LCCH1X=GS1.1.1631388103.11.0.1631388103.0; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1733508529.1620259566; _gid=GA1.2.18082541.1631388105; session=.eJwNyrEOgjAQANBfMTc7KMJCwoApEkl6LEXCLUTbRlooMQSFQPh3Wd70Vqg_enDPXvcjhOPw1UdQ-YkDNQ.YT0DBA.IsbCVSlbjfKGVp8ONzK0IpEZzZ8",
            "origin": "https://aminoapps.com/",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-ch-ua": '";Not A Brand";v="99", "Chromium";v="94"',
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.104 Safari/537.36",
            "x-requested-with": "xmlhttprequest"
        }
        if data:
            if isinstance(data, dict): data = json.dumps(data)
            self.headers["Content-Length"] = str(len(data))
            self.headers["NDC-MSG-SIG"] = base64.b64encode(b"\x22" + hmac.new(bytes.fromhex("307c3c8cd389e69dc298d951341f88419a8377f4"), data.encode(), sha1).digest()).decode()
        if sid:
            self.headers["NDCAUTH"] = f"sid={self.sid}"
            self.web_headers["cookie"] = f"sid={self.sid}"
        if type: self.headers["Content-Type"] = type
        if userId: self.headers["AUID"] = userId


# =========== TAPJOY HEADERS ==============
# from SAmino, by SirLez, with Kapi's Headers
class AdHeaders:
    def __init__(self, target: str = None):
        auth = base64.b64encode(f"5bb5349e1c9d440006750680:{str(uuid4())}".encode()).decode()
        self.data = {
            "reward": {
                "ad_unit_id": "t00_tapjoy_android_master_checkinwallet_rewardedvideo_322",
                "credentials_type": "publisher",
                "custom_json": {
                    "hashed_user_id": None
                },
                "demand_type": "sdk_bidding",
                "event_id": f"{str(uuid4())}",
                "network": "tapjoy",
                "placement_tag": "default",
                "reward_name": "Amino Coin",
                "reward_valid": "true",
                "reward_value": 2,
                "shared_id": "a0188294-b46b-4b3e-ab7e-3983e5b0adae",
                "version_id": "1569147951493",
                "waterfall_id": "a0188294-b46b-4b3e-ab7e-3983e5b0adae"
            },
            "app": {
                "bundle_id": "com.narvii.amino.master",
                "current_orientation": "portrait",
                "release_version": "3.4.33587",
                "user_agent": "Dalvik\/2.1.0 (Linux; U; Android 10; POCO F1 Build\/QQ3A.200805.001; com.narvii.amino.master\/3.4.33587)"
            },
            "date_created": 1635009572,
            "device_user": {
                "country": "BR",
                "device": {
                    "architecture": "aarch64",
                    "carrier": {
                        "country_code": 724,
                        "name": "CLARO BR",
                        "network_code": 0
                    },
                    "is_phone": "true",
                    "model": "POCO F1",
                    "model_type": "Xiaomi",
                    "operating_system": "android",
                    "operating_system_version": "29",
                    "screen_size": {
                        "height": 2032,
                        "resolution": 2.625,
                        "width": 1080
                    }
                },
                "do_not_track": "false",
                "idfa": "40f5b23d-4262-4c5e-93e9-beb559ebdb0a",
                "ip_address": "",
                "locale": "pt",
                "timezone": {
                    "location": "America\/Sao_Paulo",
                    "offset": "BRT"
                },
                "volume_enabled": "true"
            },
            "session_id": "1c6fd343-144e-4d92-ab15-0f3231d8b61a",
        }
        self.headers = {
            "Authorization": f"Basic {auth}",
            "X-Tapdaq-SDK-Version": "android-sdk_7.1.1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; POCO F1 Build/QQ3A.200805.001; com.narvii.amino.master/3.4.33587)",
            "Host": "ads.tapdaq.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        if target: self.data["reward"]["custom_json"]["hashed_user_id"] = target
