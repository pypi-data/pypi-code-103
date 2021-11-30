# ------------------------- Hydrochloric.py (PRIVATE) v0.8.1b -------------------------
import random
import string
from uuid import UUID, uuid4

import aminos
import requests
import os
import io
from .src import headers, didgen, exceptions, exceptions_v2, objects, debugs
from . import settings
import threading
import zipfile
import json
from functools import reduce
from os import urandom
import base64
from base64 import b64decode
from binascii import hexlify
from locale import getdefaultlocale as locale
from time import timezone, sleep
from time import time as timestamp
from typing import BinaryIO, Tuple
from .socket import Callbacks, SocketHandler


#   , _           _
#   | \ \_ , - ~/        , - - .
#   /  _    _    |      /    , - '   Made by:
#   \      _T_/ -._(    (         Kapidev#4448
#   /                   `.     \                 In collaboration with:
# |                     __ \   |             Slimakoi#6422 & Syscall0#3550
#   \   \    ,      /           |
#     |  |    |  -_ \___     /
#   ( ( _ / ` (_____ , - '

#  (っ•̀ω•̀)╮ This library is sacred af so please do not share it. 

# ============ LIBRARY BELOW ============

#              Please, do not change anything 
#      below, else your library probably will stop
#                                   working.

# ============= CLIENT CLASS ============

class Client(Callbacks, SocketHandler):
    def __init__(self, deviceId: str = None, proxy: bool = False, debugmode: bool = False, socket_debug: bool = False, exceptV2: bool = False, lang: str = "en-US"):
        if debugmode is True:
            debugs.enabled = True
        SocketHandler.__init__(self, self, socket_trace=False, socket_debug=socket_debug)
        Callbacks.__init__(self, self)

        self.headers()["NDCLANG"] = lang[0:lang.index("-")]
        self.headers()["Accept-Language"] = lang
        self.language = lang
        self.exceptV2 = exceptV2
        self.authenticated = False
        self.web_authenticated = False
        self.api = "https://service.narvii.com/api/v1"
        self.email = None
        self.password = None

        if deviceId is None:
            if debugs.enabled is True:
                debugs.DebugMode(data=f"Found no manually input DeviceIDs! Using generator instead...", type="Warning")
            deviceId = didgen.Didgen().deviceId
            headers.deviceId = deviceId
            if debugs.enabled is True:
                debugs.DebugMode(data=f"Generated DeviceID! : {headers.deviceId}", type="Success")
        else:
            headers.deviceId = deviceId
            if debugs.enabled is True:
                debugs.DebugMode(data=f"Using manually input DeviceID... : {headers.deviceId}", type="Info")

        # ======== PROXY HANDLER ========
        # by: Syscall0#3550

        if proxy is True:
            def get_proxy_session():
                session = requests.session()
                # Tor uses the 9050 port as the default socks port
                session.proxies = {'http': 'socks5://127.0.0.1:9050',
                                   'https': 'socks5://127.0.0.1:9050'}
                # You can find all in https://www.socks-proxy.net/
                # ip = "186.126.186.151"
                # port = "1080"
                # proxy_url = f'socks4://{ip}:{port}'
                # session.proxies = {'http': proxy_url,
                #                    'https': proxy_url}
                return session

            self.session = get_proxy_session()
            print(
                f"\n \33[48;5;56m\33[38;5;231m PROXY IP ❯ \033[0;0m\33[48;5;235m\33[38;5;99m {self.session.get('https://ifconfig.me/ip').text} \033[0;0m ")

        else:
            self.session = requests.session()

    def handle_socket_message(self, data):
        return self.resolve(data)

    # =========== SELF DEFINITIONS ============
    def userId(self):
        return headers.userId

    def deviceId(self):
        return headers.deviceId

    def sid(self):
        return headers.sid

    def ad_headers(self, target: str = None):
        if target:
            return headers.AdHeaders(target=target)
        else:
            return headers.AdHeaders()

    def web_headers(self):
        return headers.Headers().web_headers

    def headers(self, data=None, type: str = None):
        if data and type: return headers.Headers(data=data).headers
        elif data: return headers.Headers(data=data).headers
        elif type: return headers.Headers().headers
        else: return headers.Headers().headers

    # ============= USEFUL TOOLS ============
    # From SAmino
    def gen_captcha(self):
        return "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + "_-", k=462)).replace("--", "-")

    def decode_sid(self, sid: str) -> dict:
        return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

    def sid_to_uid(self, sid: str) -> str:
        return self.decode_sid(sid)["2"]

    def sid_to_ip_address(self, sid: str) -> str:
        return self.decode_sid(sid)["4"]

    def colored(self, r, g, b, text, rb: int = None, gb: int = None, bb: int = None):
        if rb is None and gb is None and bb is None: return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)
        else: return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m{}\033[0m".format(r, g, b, rb, gb, bb, text)

    # ================ LOGIN ================
    def login(self, email: str = None, password: str = None, sid: str = None, asWeb: bool = False, asDeviceIdGen: bool = False):
        # returns json loadable text
        if sid:
            headers.sid = sid
            if debugs.enabled is True: debugs.DebugMode(data=f"Updated SID Value to: {headers.sid}", type="Info")
            response = self.session.get("https://service.narvii.com/api/v1/g/s/device/dev-options", headers=self.headers())
            if json.loads(response.content)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
                else: exceptions.CheckException(response.json())
                return response.text
            else:
                userId = self.sid_to_uid(sid)
                if debugs.enabled is True: debugs.DebugMode(data=f"Updated UserID Value to: {headers.userId}", type="Info")
                self.authenticated = True
                headers.userId = userId
                if settings.socketAuto is True: self.start_socket(asWeb=settings.sAutoAsWeb)
                if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
                return response.text
        elif asWeb or asDeviceIdGen:
            self.email = email
            self.password = password
            data = {
                "auth_type": 0,
                "email": email,
                "recaptcha_challenge": self.gen_captcha(),
                "recaptcha_version": "v3",
                "secret": password
            }
            response = self.session.post("https://aminoapps.com/api/auth", json=data, headers=self.web_headers())
            try:
                headers.sid = response.headers["set-cookie"].split("sid=")[1]
                headers.sid = headers.sid[0: headers.sid.index(";")]
                headers.userId = response.json()["result"]["uid"]
                if debugs.enabled is True: debugs.DebugMode(data=f"Updated UserID Value to: {headers.userId}", type="Info")
                if debugs.enabled is True: debugs.DebugMode(data=f"Updated SID Value to: {headers.sid}", type="Info")
                self.authenticated = True
                self.web_authenticated = True
                if settings.socketAuto is True: self.start_socket(asWeb=settings.sAutoAsWeb)
                if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
                return response.text
            except:
                if debugs.enabled is True: debugs.DebugMode(data=f"Found an unverified account! Generating DeviceID...", type="Warning")
                try:
                    if asDeviceIdGen:
                        generated = str(response.json()).split("deviceid=")[1].split("'")[0]
                        if debugs.enabled is True: debugs.DebugMode(data=f"Successfully Generated Device ID! : {generated}", type="Success")
                        return generated
                    else: pass
                except:
                    exceptions_v2.ExceptionList().failedWebLogin()
                    return response.text
        else:
            self.email = email
            self.password = password
            data = json.dumps({
                "email": email,
                "v": 2,
                "secret": f"0 {password}",
                "deviceID": self.deviceId(),
                "clientType": 100,
                "action": "normal",
                "timestamp": int(timestamp() * 1000)
            })
            response = self.session.post(f"{self.api}/g/s/auth/login", headers=self.headers(data=data), data=data)
            if response.json()["api:statuscode"] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
                else: exceptions.CheckException(response.json())
                return response.text
            else:
                self.authenticated = True
                headers.sid = response.json()["sid"]
                headers.userId = response.json()["account"]["uid"]
                if debugs.enabled is True: debugs.DebugMode(data=f"Updated UserID Value to: {headers.userId}", type="Info")
                if debugs.enabled is True: debugs.DebugMode(data=f"Updated SID Value to: {headers.sid}", type="Info")
                if settings.socketAuto is True: self.start_socket(asWeb=settings.sAutoAsWeb)
                if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =============== LOGOUT ================

    def logout(self):
        if self.web_authenticated:
            response = self.session.post("https://aminoapps.com/api/logout", headers=self.web_headers())
            if response.status_code != 200:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                self.web_authenticated = False
                self.authenticated = False
                headers.userId = None
                headers.sid = None
                if debugs.enabled is True:
                    debugs.DebugMode(data=f"Updated UserID Value to: {headers.userId}", type="Info")
                if debugs.enabled is True:
                    debugs.DebugMode(data=f"Updated SID Value to: {headers.sid}", type="Info")
                if settings.socketAuto is True:
                    self.close()
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text
        else:
            if self.authenticated:
                data = json.dumps({
                    "deviceID": self.deviceId(),
                    "clientType": 100,
                    "timestamp": int(timestamp() * 1000)
                })

                response = self.session.post(f"{self.api}/g/s/auth/logout", headers=self.headers(data=data), data=data)
                if response.json()['api:statuscode'] != 0:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(response.json())
                    return response.text
                else:
                    self.authenticated = False
                    headers.userId = None
                    headers.sid = None
                    if debugs.enabled is True:
                        debugs.DebugMode(data=f"Updated UserID Value to: {headers.userId}", type="Info")
                    if debugs.enabled is True:
                        debugs.DebugMode(data=f"Updated SID Value to: {headers.sid}", type="Info")
                    if settings.socketAuto is True:
                        self.close()
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")
                    return response.text
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()

    # ========= REQUEST VERIFY CODE =========

    def request_verify_code(self, email: str = None, resetPassword: bool = False):
        if not email:
            email = self.email
        data = {
            "identity": email,
            "type": 1,
            "deviceID": self.deviceId()
        }

        if resetPassword is True:
            data["level"] = 2
            data["purpose"] = "reset-password"

        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/auth/request-security-validation",
                                     headers=self.headers(data=data), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # =============== REGISTER ==============

    def register(self, nickname: str, email: str, password: str, verificationCode: str, asWeb: bool = False):
        if asWeb is True:
            data = {
                'email': email,
                'nickname': nickname,
                'phoneNumber': "",
                'secret2': password,
                'validationContext': {
                    'data': {'code': verificationCode},
                    'code': verificationCode,
                    'identity': email,
                    'type': 1,
                    '__original': {
                        'data': {'code': verificationCode},
                        'code': verificationCode,
                        'identity': email,
                        'type': 1,
                        '__response': {}
                    }
                }
            }
            response = self.session.post("https://aminoapps.com/api/register", json=data, headers=self.web_headers())
            try:
                if response.json()["result"]['api:message'] == "OK":
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(response.json())
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            data = json.dumps({
                "secret": f"0 {password}",
                "deviceID": self.deviceId(),
                "email": email,
                "clientType": 100,
                "nickname": nickname,
                "latitude": 0,
                "longitude": 0,
                "address": None,
                "clientCallbackURL": "narviiapp://relogin",
                "validationContext": {
                    "data": {
                        "code": verificationCode
                    },
                    "type": 1,
                    "identity": email
                },
                "type": 1,
                "identity": email,
                "timestamp": int(timestamp() * 1000)
            })
            response = self.session.post(f"{self.api}/g/s/auth/register", headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ===== [ WEB ONLY ] REGISTER CHECK =======

    def register_check(self, email: str, password: str):
        data = json.dumps({
            'email': email,
            'phoneNumber': "",
            'secret': password
        })
        response = self.session.post("https://aminoapps.com/api/register-check", data=data, headers=self.web_headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.json()
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.json()

    # ========== RESTORE ACCOUNT ===========

    def restore(self, email: str, password: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": self.deviceId(),
            "email": email,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/g/s/account/delete-request/cancel", headers=self.headers(data=data),
                                     data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ========== CONFIGURE ACCOUNT =========

    def configure(self, age: int, gender: str):
        if self.authenticated:
            if gender.lower() == "male":
                gender = 1
            elif gender.lower() == "female":
                gender = 2
            elif gender.lower() == "non-binary":
                gender = 255
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if age <= 12:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().ageTooLow()
                else:
                    raise exceptions.AgeTooLow()

            data = json.dumps({
                "age": age,
                "gender": gender,
                "timestamp": int(timestamp() * 1000)
            })

            response = self.session.post(f"{self.api}/g/s/persona/profile/basic", data=data,
                                         headers=self.headers(data=data))
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()

    # =========== VERIFY ACCOUNT ============

    def verify(self, email: str, verificationCode: str, asWeb: bool = False):
        if asWeb is True:
            data = json.dumps({
                'validationContext': {'data': {'code': verificationCode},
                                      'identity': email,
                                      'type': 1,
                                      'verifyInfoKey': None}})

            response = self.session.post("https://aminoapps.com/api/auth/check-security-validation", data=data,
                                         headers=self.web_headers())
            if response.status_code != 200:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.json()
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.json()

        else:
            data = json.dumps({
                "validationContext": {
                    "type": 1,
                    "identity": email,
                    "data": {"code": verificationCode}},
                "deviceID": self.deviceId(),
                "timestamp": int(timestamp() * 1000)
            })
            response = self.session.post(f"{self.api}/g/s/auth/check-security-validation",
                                         headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== ACTIVATE ACCOUNT ===========

    def activate_account(self, email: str, verificationCode: str):
        data = json.dumps({
            "type": 1,
            "identity": email,
            "data": {"code": verificationCode},
            "deviceID": self.deviceId()
        })

        response = self.session.post(f"{self.api}/g/s/auth/activate-email", headers=self.headers(data=data), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # =========== DELETE ACCOUNT ============
    # Provided by 𝑰 𝑵 𝑻 𝑬 𝑹 𝑳 𝑼 𝑫 𝑬#4082

    def delete_account(self):
        if self.authenticated:
            data = json.dumps({
                "deviceID": self.deviceId(),
                "secret": f"0 {self.password()}"
            })

            response = self.session.post(f"{self.api}/g/s/account/delete-request", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()

    # ========== CHANGE_PASSWORD ==========

    def change_password(self, verificationCode: str, email: str = None, password: str = None):
        if not email:
            email = self.email
        if not password:
            password = self.password
        data = json.dumps({
            "updateSecret": f"0 {password}",
            "emailValidationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email,
                "level": 2,
                "deviceID": self.deviceId()
            },
            "phoneNumberValidationContext": None,
            "deviceID": self.deviceId()
        })

        response = self.session.post(f"{self.api}/g/s/auth/reset-password", headers=self.headers(data=data), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ========== GET ACCOUNT INFO ============

    def get_account_info(self):
        # Use json.loads(get_account_info())["account"] to get only account info
        if self.authenticated:
            response = self.session.get(f"{self.api}/g/s/account", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.UserProfile(response.json()["account"]).UserProfile
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()

    # ============ GET EVENTLOG =============

    def get_eventlog(self):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/eventlog/profile?language=en", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== VALIDATE DEVICEID ============

    def validate_deviceId(self, deviceId: str = None):
        if not deviceId:
            deviceId = self.deviceId()
        data = json.dumps({
            "deviceID": deviceId,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -timezone // 1000,
            "systemPushEnabled": True,
            "locale": locale()[0],
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/g/s/device", headers=self.headers(data=data), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ============= UPLOAD MEDIA ============

    def upload_media(self, file: BinaryIO, fileType: str):
        # Use json.loads(upload_media())["mediaValue"] to obtain mediaValue
        type = ""
        if fileType == "audio":
            type = "audio/aac"
        elif fileType == "image":
            type = "image/jpg"
        else:
            os._exit(0)

        data = file.read()
        response = self.session.post(f"{self.api}/g/s/media/upload", data=data, headers=self.headers(data=data, type=type))
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.json()["mediaValue"]

    # ========= JOINED COMMUNITIES ============

    def sub_clients(self, start: int = 0, size: int = 25):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.CommunityList(response.json()["communityList"]).CommunityList

    def sub_clients_profile(self, start: int = 0, size: int = 25):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.json()["userInfoInCommunities"]

    # ============= USER PROFILE ============

    def get_user_info(self, userId: str = None):
        if not userId:
            userId = headers.userId
        # Use json.loads(user_profile())["userProfile"] to get only user info
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfile(response.json()["userProfile"]).UserProfile

    # ========== GET CHAT THREADS ===========

    def get_chat_threads(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/g/s/chat/thread?type=joined-me&start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.ThreadList(response.json()["threadList"]).ThreadList

    def get_chat_thread(self, chatId: str):
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Thread(response.json()["thread"]).Thread

    # =========== GET CHAT USERS ============

    def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        # Use json.loads(get_chat_users())["memberList"] to get only member list
        response = self.session.get(
            f"{self.api}/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2",
            headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(response.json()["memberList"]).UserProfileList

    # ============== JOIN CHAT ==============

    def join_chat(self, chatId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{headers.userId}",
                                         headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= LEAVE CHAT ==============

    def leave_chat(self, chatId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.delete(f"{self.api}/g/s/chat/thread/{chatId}/member/{headers.userId}",
                                           headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= START CHAT ==============

    def start_chat(self, invited: [str, list], message: str, title: str, description: str, isGlobal: bool = False,
                   showInGlobal: bool = False):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if isinstance(invited, str):
                userIds = [invited]
            elif isinstance(invited, list):
                userIds = invited
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().wrongType()
                else:
                    raise exceptions.WrongType()

            data = {
                "title": title,
                "inviteeUids": userIds,
                "initialMessageContent": message,
                "content": description,
                "timestamp": int(timestamp() * 1000)
            }

            if isGlobal is True:
                data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
            else:
                data["type"] = 0

            if showInGlobal is True:
                data["publishToGlobal"] = 1
            else:
                data["publishToGlobal"] = 0

            data = json.dumps(data)

            response = self.session.post(f"{self.api}/g/s/chat/thread", data=data, headers=self.headers(data=data))
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ INVITE TO CHAT ============

    def invite_to_chat(self, userId: [str, list], chatId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if isinstance(userId, str):
                userIds = [userId]
            elif isinstance(userId, list):
                userIds = userId
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().wrongType()
                else:
                    raise exceptions.WrongType()

            data = json.dumps({
                "uids": userIds,
                "timestamp": int(timestamp() * 1000)
            })

            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/invite",
                                         headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ KICK FROM CHAT============

    def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if allowRejoin:
                allowRejoin = 1
            if not allowRejoin:
                allowRejoin = 0
            response = self.session.delete(
                f"{self.api}/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}",
                headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== GET CHAT MESSAGES =========

    def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):
        if pageToken is not None:
            url = f"{self.api}/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"

        response = self.session.get(url, headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.GetMessages(response.json()).GetMessages

    # ========== GET MESSAGE INFO ============

    def get_message_info(self, chatId: str, messageId: str):
        # Use json.loads(get_message_info())["message"] to get only message info.
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Message(response.json()["message"]).Message

    # ========== GET COMMUNITY INFO =========

    def get_community_info(self, comId: str):
        # Use json.loads(get_community_info())["community"] to get only community info
        response = self.session.get(
            f"{self.api}/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount",
            headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Community(response.json()["community"]).Community

    # ========== SEARCH COMMUNITY =========

    def search_community(self, aminoId: str):
        # Use com["refObject"] for com in response to get only community list.
        response = self.session.get(f"{self.api}/g/s/search/amino-id-and-link?q={aminoId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            result = response.json()["resultList"]
            if len(result) == 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().communityNotFound()
                else:
                    raise exceptions.CommunityNotFound(aminoId)
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.CommunityList([com["refObject"] for com in response]).CommunityList

    # ========= GET USER FOLLOWING ==========

    def get_user_following(self, userId: str = None, start: int = 0, size: int = 25):
        # Use json.loads(get_user_following())["userProfileList"] to get only user following list
        if not userId:
            if not self.authenticated:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()
            else:
                userId = self.userId()
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/joined?start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(response.json()["userProfileList"]).UserProfileList

    # ========= GET USER FOLLOWERS ==========

    def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        # Use json.loads(get_user_followers())["userProfileList"] to get only user followers list
        if not userId:
            if not self.authenticated:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()
            else:
                userId = self.userId()
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/member?start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(response.json()["userProfileList"]).UserProfileList

    # =========== GET USER VISITORS ============

    def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        if not userId:
            if not self.authenticated:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()
            else:
                userId = self.userId()
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/visitors?start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.VisitorsList(response.json()).VisitorsList

    # ========== GET BLOCKED USERS ============

    def get_blocked_users(self, start: int = 0, size: int = 25):
        # Use json.loads(get_blocked_users())["userProfileList"] to get only user blocked list
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/block?start={start}&size={size}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.UserProfileList(response.json()["userProfileList"]).UserProfileList

    # ========= GET BLOCKING USERS ============

    def get_blocking_users(self, start: int = 0, size: int = 25):
        # Use json key ["blockerUidList"] to get only blocker list
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/block/full-list?start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.json()["blockerUidList"]

    # ============ GET BLOG INFO===============

    def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = self.session.get(f"{self.api}/g/s/blog/{blogId}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.GetBlogInfo(response.json()).GetBlogInfo

        elif wikiId:
            response = self.session.get(f"{self.api}/g/s/item/{wikiId}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.GetWikiInfo(response.json()).GetWikiInfo

        elif fileId:
            # Use json key ["file"] to get only file info
            response = self.session.get(f"{self.api}/g/s/shared-folder/files/{fileId}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.SharedFolderFile(response.json()["file"]).SharedFolderFile
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

    # ========= GET BLOG COMMENTS ============

    def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None,
                          sorting: str = "newest", start: int = 0, size: int = 25):
        # Use json key ["commentList"] to get only comment list
        if sorting == "newest":
            sorting = "newest"
        elif sorting == "oldest":
            sorting = "oldest"
        elif sorting == "top":
            sorting = "vote"
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = self.session.get(
                f"{self.api}/g/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        elif wikiId:
            response = self.session.get(
                f"{self.api}/g/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        elif fileId:
            response = self.session.get(
                f"{self.api}/g/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommentList(response.json()["commentList"]).CommentList

    # ========= GET WALL COMMENTS ============

    def get_wall_comments(self, sorting: str, userId: str = None, start: int = 0, size: int = 25):
        # Use json key ["commentList"] to get only user comment list
        if not userId:
            if not self.authenticated:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()
            else:
                userId = self.userId()
        if sorting.lower() == "newest":
            sorting = "newest"
        elif sorting.lower() == "oldest":
            sorting = "oldest"
        elif sorting.lower() == "top":
            sorting = "vote"
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        response = self.session.get(
            f"{self.api}/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}",
            headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommentList(response.json()["commentList"]).CommentList

    # ========= [ TAPJOY ] WATCH AD =============
    # By Marshall (Smile, Texaz) (from SAmino)

    def watch_ad(self, userId: str = None):
        if not userId:
            if not self.authenticated:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().notLoggedIn()
                else:
                    raise exceptions.NotLoggedIn()
            else:
                userId = self.userId()
        response = self.session.post("https://ads.tapdaq.com/v4/analytics/reward", headers=self.ad_headers().headers,
                                     json=self.ad_headers(target=userId).data)
        if response.status_code != 204:
            exceptions_v2.ExceptionList(response.text)
        if debugs.enabled is True:
            debugs.DebugMode(data=response.text, type="Success")
        return response.text

    # ========== [ AMINO ] WATCH AD =============

    def amino_watch_ad(self):
        response = self.session.post(f"{self.api}/g/s/wallet/ads/video/start", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ================ FLAG ===================

    def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None,
             asGuest: bool = False):
        if reason is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().reasonNeeded()
            else:
                raise exceptions.ReasonNeeded()
        if flagType is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().flagTypeNeeded()
            else:
                raise exceptions.FlagTypeNeeded()
        data = {
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        }
        if userId:
            data["objectId"] = userId
            data["objectType"] = 0
        elif blogId:
            data["objectId"] = blogId
            data["objectType"] = 1
        elif wikiId:
            data["objectId"] = wikiId
            data["objectType"] = 2
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        if asGuest:
            flg = "g-flag"
        else:
            flg = "flag"

        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/{flg}", data=data, headers=self.headers(data=data))
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ============ SEND MESSAGE ==============

    def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None,
                     fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None,
                     embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None,
                     embedContent: str = None, embedImage: BinaryIO = None):
        #        **Parameters**
        #            - **message** : Message to be sent
        #            - **chatId** : ID of the Chat.
        #            - **file** : File to be sent.
        #            - **fileType** : Type of the file.
        #                - ``audio``, ``image``, ``gif``
        #            - **messageType** : Type of the Message.
        #            - **mentionUserIds** : List of User IDS to mention. '@' needed in the Message.
        #            - **replyTo** : Message ID to reply to.
        #            - **stickerId** : Sticker ID to be sent.
        #            - **embedTitle** : Title of the Embed.
        #            - **embedContent** : Content of the Embed.
        #            - **embedLink** : Link of the Embed.
        #            - **embedImage** : Image of the Embed.
        #            - **embedId** : ID of the Embed.
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if message is not None and file is None:
                message = message.replace("<$", "‎‏").replace("$>", "‬‭")

            mentions = []
            if mentionUserIds:
                for mention_uid in mentionUserIds:
                    mentions.append({"uid": mention_uid})

            if embedImage:
                embedImage = [[100, self.upload_media(embedImage, "image"), None]]

            data = {
                "type": messageType,
                "content": message,
                "clientRefId": int(timestamp() / 10 % 1000000000),
                "attachedObject": {
                    "objectId": embedId,
                    "objectType": embedType,
                    "link": embedLink,
                    "title": embedTitle,
                    "content": embedContent,
                    "mediaList": embedImage
                },
                "extensions": {"mentionedArray": mentions},
                "timestamp": int(timestamp() * 1000)
            }

            if replyTo: data["replyMessageId"] = replyTo

            if stickerId:
                data["content"] = None
                data["stickerId"] = stickerId
                data["type"] = 3

            if file:
                data["content"] = None
                if fileType == "audio":
                    data["type"] = 2
                    data["mediaType"] = 110

                elif fileType == "image":
                    data["mediaType"] = 100
                    data["mediaUploadValueContentType"] = "image/jpg"
                    data["mediaUhqEnabled"] = True

                elif fileType == "gif":
                    data["mediaType"] = 100
                    data["mediaUploadValueContentType"] = "image/gif"
                    data["mediaUhqEnabled"] = True

                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        return exceptions_v2.ExceptionList().specifyType()
                    else:
                        raise exceptions.SpecifyType()

                data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/message",
                                         headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== DELETE MESSAGE =============

    def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if not asStaff:
                response = self.session.delete(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}",
                                               headers=self.headers())
            else:
                data = {
                    "adminOpName": 102,
                    "adminOpNote": {"content": reason},
                    "timestamp": int(timestamp() * 1000)
                }

                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}/admin",
                                             headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ MARK AS READ ===============

    def mark_as_read(self, chatId: str, messageId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({
                "messageId": messageId,
                "timestamp": int(timestamp() * 1000)
            })
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/mark-as-read", headers=self.headers(),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============== EDIT CHAT ================

    def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None,
                  icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None,
                  coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None,
                  publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None,
                  fansOnly: bool = None):
        #        Send a Message to a Chat.

        #        **Parameters**
        #            - **chatId** : ID of the Chat.
        #            - **title** : Title of the Chat.
        #            - **content** : Content of the Chat.
        #            - **icon** : Icon of the Chat.
        #            - **backgroundImage** : Url of the Background Image of the Chat.
        #            - **announcement** : Announcement of the Chat.
        #            - **pinAnnouncement** : If the Chat Announcement should Pinned or not.
        #            - **coHosts** : List of User IDS to be Co-Host.
        #            - **keywords** : List of Keywords of the Chat.
        #            - **viewOnly** : If the Chat should be on View Only or not.
        #            - **canTip** : If the Chat should be Tippable or not.
        #            - **canInvite** : If the Chat should be Invitable or not.
        #            - **fansOnly** : If the Chat should be Fans Only or not.
        #            - **publishToGlobal** : If the Chat should show on Public Chats or not.
        #            - **doNotDisturb** : If the Chat should Do Not Disturb or not.
        #            - **pinChat** : If the Chat should Pinned or not.

        #        **Returns**
        #            - **Success** : 200 (int)

        #            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`

        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:

            data = {"timestamp": int(timestamp() * 1000)}

            if title: data["title"] = title
            if content: data["content"] = content
            if icon: data["icon"] = icon
            if keywords: data["keywords"] = keywords
            if announcement: data["extensions"] = {"announcement": announcement}
            if pinAnnouncement: data["extensions"] = {"pinAnnouncement": pinAnnouncement}
            if fansOnly: data["extensions"] = {"fansOnly": fansOnly}

            if publishToGlobal: data["publishToGlobal"] = 0
            if not publishToGlobal: data["publishToGlobal"] = 1

            res = []

            if doNotDisturb is not None:
                if doNotDisturb:
                    data = json.dumps({"alertOption": 2, "timestamp": int(timestamp() * 1000)})
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/alert",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

                if not doNotDisturb:
                    data = json.dumps({"alertOption": 1, "timestamp": int(timestamp() * 1000)})
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/alert",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

            if pinChat is not None:
                if pinChat:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/pin", data=data,
                                                 headers=self.headers())
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

                if not pinChat:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/unpin", data=data,
                                                 headers=self.headers())
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

            if backgroundImage is not None:
                data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(timestamp() * 1000)})
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/background",
                                             data=data, headers=self.headers(data=data))
                if response.json()['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(response.json()))
                else:
                    res.append(response.json()['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if coHosts is not None:
                data = json.dumps({"uidList": coHosts, "timestamp": int(timestamp() * 1000)})
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/co-host", data=data,
                                             headers=self.headers(data=data))
                if response.json()['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(response.json()))
                else:
                    res.append(response.json()['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if viewOnly is not None:
                if viewOnly:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/view-only/enable", data=data,
                                                 headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

                if not viewOnly:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/view-only/disable", data=data,
                                                 headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

            if canInvite is not None:
                if canInvite:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/members-can-invite/enable",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

                if not canInvite:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/members-can-invite/disable",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

            if canTip is not None:
                if canTip:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/tipping-perm-status/enable",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

                if not canTip:
                    response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/tipping-perm-status/disable",
                                                 data=data, headers=self.headers(data=data))
                    if response.json()['api:statuscode'] != 0:
                        res.append(exceptions.CheckException(response.json()))
                    else:
                        res.append(response.json()['api:statuscode'])
                        if debugs.enabled is True:
                            debugs.DebugMode(data=response.text, type="Success")

            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                res.append(exceptions.CheckException(response.json()))
            else:
                res.append(response.json()['api:statuscode'])
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")

            return res

    # ============= VISIT PROFILE ===============

    def visit(self, userId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/user-profile/{userId}?action=visit", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============== SEND COINS ===============

    def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None,
                   transactionId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            url = None
            if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

            data = {
                "coins": coins,
                "tippingContext": {"transactionId": transactionId},
                "timestamp": int(timestamp() * 1000)
            }

            if blogId is not None: url = f"{self.api}/g/s/blog/{blogId}/tipping"
            if chatId is not None: url = f"{self.api}/g/s/chat/thread/{chatId}/tipping"
            if objectId is not None:
                data["objectId"] = objectId
                data["objectType"] = 2
                url = f"{self.api}/g/s/tipping"

            if url is None:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            data = json.dumps(data)
            response = self.session.post(url, headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= FOLLOW USER ===============

    def follow(self, userId: [str, list]):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if isinstance(userId, str):
                response = self.session.post(f"{self.api}/g/s/user-profile/{userId}/member", headers=self.headers())
            elif isinstance(userId, list):
                data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
                response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/joined",
                                             headers=self.headers(data=data), data=data)
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().wrongType()
                else:
                    raise exceptions.WrongType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ UNFOLLOW USER =============

    def unfollow(self, userId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.delete(f"{self.api}/g/s/user-profile/{userId}/member/{self.userId}",
                                           headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= BLOCK USER ================

    def block(self, userId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/g/s/block/{userId}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ UNBLOCK USER ==============

    def unblock(self, userId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.delete(f"{self.api}/g/s/block/{userId}", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== JOIN COMMUNITY =============

    def join_community(self, comId: str, invitationId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = {"timestamp": int(timestamp() * 1000)}
            if invitationId: data["invitationId"] = invitationId

            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{comId}/s/community/join", data=data,
                                         headers=self.headers(data=data))
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ======= REQUEST JOIN COMMUNITY  =========

    def request_join_community(self, comId: str, message: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({"message": message, "timestamp": int(timestamp() * 1000)})
            response = self.session.post(f"{self.api}/x{comId}/s/community/membership-request", data=data,
                                         headers=self.headers(data=data))
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== LEAVE COMMUNITY =============

    def leave_community(self, comId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/x{comId}/s/community/leave", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== FLAG COMMUNITY ============

    def flag_community(self, comId: str, reason: str, flagType: int, isGuest: bool = False):
        if reason is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().reasonNeeded()
            else:
                raise exceptions.ReasonNeeded()
        if flagType is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().flagTypeNeeded()
            else:
                raise exceptions.FlagTypeNeeded()

        data = json.dumps({
            "objectId": comId,
            "objectType": 16,
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        })

        if isGuest:
            flg = "g-flag"
        else:
            flg = "flag"

        response = self.session.post(f"{self.api}/x{comId}/s/{flg}", data=data, headers=self.headers(data=data))
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ============= EDIT PROFILE ===============

    def edit_profile(self, nickname: str = None, biography: str = None, icon: BinaryIO = None,
                     backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None):
        #        **Parameters**
        #            - **nickname** : Nickname of the Profile.
        #            - **content** : Biography of the Profile.
        #            - **icon** : Icon of the Profile.
        #            - **backgroundImage** : Url of the Background Picture of the Profile.
        #            - **backgroundColor** : Hexadecimal Background Color of the Profile.
        #            - **defaultBubbleId** : Chat bubble ID.
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = {
                "address": None,
                "latitude": 0,
                "longitude": 0,
                "mediaList": None,
                "eventSource": "UserProfileView",
                "timestamp": int(timestamp() * 1000)
            }

            if nickname: data["nickname"] = nickname
            if icon: data["icon"] = self.upload_media(icon, "image")
            if biography: data["content"] = biography
            if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
            if backgroundImage: data["extensions"] = {
                "style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
            if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== SET PRIVACY STATUS ============

    def set_privacy_status(self, isAnonymous: bool = False, getNotifications: bool = False):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = {"timestamp": int(timestamp() * 1000)}

            if not isAnonymous: data["privacyMode"] = 1
            if isAnonymous: data["privacyMode"] = 2
            if not getNotifications: data["notificationStatus"] = 2
            if getNotifications: data["privacyMode"] = 1

            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/account/visit-settings", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= SET AMINO ID ===============

    def set_amino_id(self, aminoId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({"aminoId": aminoId, "timestamp": int(timestamp() * 1000)})
            response = self.session.post(f"{self.api}/g/s/account/change-amino-id", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ======= GET LINKED COMMUNITIES ==========

    def get_linked_communities(self, userId: str):

        #        Get a List of Linked Communities of an User.

        #        **Parameters**
        #            - **userId** : ID of the User.

        #        **Returns**
        #            - **Success** : :meth:`Community List <amino.lib.src.objects.CommunityList>`

        #            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`

        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/linked-community", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommunityList(response.json()["linkedCommunityList"]).CommunityList

    # ======= GET UNLINKED COMMUNITIES ========

    def get_unlinked_communities(self, userId: str):

        #        Get a List of Unlinked Communities of an User.

        #        **Parameters**
        #            - **userId** : ID of the User.

        #        **Returns**
        #            - **Success** : :meth:`Community List <amino.lib.src.objects.CommunityList>`

        #            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`

        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/linked-community", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommunityList(response.json()["unlinkedCommunityList"]).CommunityList

    # ===== REORDER LINKED COMMUNITIES ========

    def reorder_linked_communities(self, comIds: list):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({"ndcIds": comIds, "timestamp": int(timestamp() * 1000)})
            response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/reorder",
                                         headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ======== ADD LINKED COMMUNITY ===========

    def add_linked_community(self, comId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/{comId}",
                                         headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ====== REMOVE LINKED COMMUNITY  ========

    def remove_linked_community(self, comId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.delete(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/{comId}",
                                           headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============== COMMENT =================

    def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if message is None:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().messageNeeded()
                else:
                    raise exceptions.MessageNeeded()

            data = {
                "content": message,
                "stickerId": None,
                "type": 0,
                "timestamp": int(timestamp() * 1000)
            }

            if replyTo: data["respondTo"] = replyTo

            if userId:
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/user-profile/{userId}/g-comment",
                                             headers=self.headers(data=data), data=data)

            elif blogId:
                data["eventSource"] = "PostDetailView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/blog/{blogId}/g-comment", headers=self.headers(data=data),
                                             data=data)

            elif wikiId:
                data["eventSource"] = "PostDetailView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/item/{wikiId}/g-comment", headers=self.headers(data=data),
                                             data=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== DELETE COMMENT =============

    def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if userId:
                response = self.session.delete(f"{self.api}/g/s/user-profile/{userId}/g-comment/{commentId}",
                                               headers=self.headers())
            elif blogId:
                response = self.session.delete(f"{self.api}/g/s/blog/{blogId}/g-comment/{commentId}",
                                               headers=self.headers())
            elif wikiId:
                response = self.session.delete(f"{self.api}/g/s/item/{wikiId}/g-comment/{commentId}",
                                               headers=self.headers())
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============== LIKE BLOG =================

    def like_blog(self, blogId: [str, list] = None, wikiId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = {
                "value": 4,
                "timestamp": int(timestamp() * 1000)
            }

            if blogId:
                if isinstance(blogId, str):
                    data["eventSource"] = "UserProfileView"
                    data = json.dumps(data)
                    response = self.session.post(f"{self.api}/g/s/blog/{blogId}/g-vote?cv=1.2",
                                                 headers=self.headers(data=data), data=data)

                elif isinstance(blogId, list):
                    data["targetIdList"] = blogId
                    data = json.dumps(data)
                    response = self.session.post(f"{self.api}/g/s/feed/g-vote", headers=self.headers(data=data),
                                                 data=data)

                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        return exceptions_v2.ExceptionList().wrongType()
                    else:
                        raise exceptions.WrongType()

            elif wikiId:
                data["eventSource"] = "PostDetailView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/item/{wikiId}/g-vote?cv=1.2",
                                             headers=self.headers(data=data), data=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= UNLIKE BLOG ===============

    def unlike_blog(self, blogId: str = None, wikiId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if blogId:
                response = self.session.delete(f"{self.api}/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView",
                                               headers=self.headers())
            elif wikiId:
                response = self.session.delete(f"{self.api}/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView",
                                               headers=self.headers())
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ LIKE COMMENT ==============

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

        #        Like a Comment on a User's Wall, Blog or Wiki.

        #        **Parameters**
        #            - **commentId** : ID of the Comment.
        #            - **userId** : ID of the User. (for Walls)
        #            - **blogId** : ID of the Blog. (for Blogs)
        #            - **wikiId** : ID of the Wiki. (for Wikis)
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = {
                "value": 4,
                "timestamp": int(timestamp() * 1000)
            }

            if userId:
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                response = self.session.post(
                    f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1",
                    headers=self.headers(data=data), data=data)

            elif blogId:
                data["eventSource"] = "PostDetailView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1",
                                             headers=self.headers(data=data), data=data)

            elif wikiId:
                data["eventSource"] = "PostDetailView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1",
                                             headers=self.headers(data=data), data=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== UNLIKE COMMENT =============

    def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            if userId:
                response = self.session.delete(
                    f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView",
                    headers=self.headers())
            elif blogId:
                response = self.session.delete(
                    f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView",
                    headers=self.headers())
            elif wikiId:
                response = self.session.delete(
                    f"{self.api}/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView",
                    headers=self.headers())
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========= GET MEMBERSHIP INFO ===========

    def get_membership_info(self):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/membership?force=true", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.Membership(response.json()).Membership

    # ======= GET T.A. ANNOUNCEMENTS ==========

    def get_ta_announcements(self, language: str = "en", start: int = 0, size: int = 25):
        # Use json key ["blogList"] to get only Blog List
        #        Get the list of Team Amino's Announcement Blogs.

        #        **Parameters**
        #            - **language** : Language of the Blogs.
        #                - ``en``, ``es``, ``pt``, ``ar``, ``ru``, ``fr``, ``de``
        #            - *start* : Where to start the list.
        #            - *size* : Size of the list.

        if language not in self.get_supported_languages(): os._exit(0)
        response = self.session.get(f"{self.api}/g/s/announcement?language={language}&start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(response.json()["blogList"]).BlogList

    # ======= GET SUPPORTED LANGUAGES ========

    def get_supported_languages(self):
        # Use json key ["supportedLanguages"] to get only supported languages list
        response = self.session.get(f"{self.api}/g/s/community-collection/supported-languages?start=0&size=100",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.json()["supportedLanguages"]

    # =========== GET WALLET INFO =============

    def get_wallet_info(self):
        # Use json key ["wallet"] to get only wallet info
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/wallet", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.WalletInfo(response.json()["wallet"]).WalletInfo

    # ========== GET WALLET HISTORY============

    def get_wallet_history(self, start: int = 0, size: int = 25):
        # Use json key ["coinHistoryList"] to get only wallet history list
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.WalletHistory(response.json()["coinHistoryList"]).WalletHistory

    # ========= USERID FROM DEVICEID ===========

    def get_from_deviceid(self, deviceId: str = None):
        # Use json key ["auid"] to get only userId
        if not deviceId:
            deviceId = self.deviceId()
        response = self.session.get(f"{self.api}/g/s/auid?deviceId={deviceId}")
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.json()["auid"]

    # ========== EXTRACT OBJECT ID ============

    def get_from_link(self, code: str):
        # Use json key ["linkInfoV2"] to get only objectId
        response = self.session.get(f"{self.api}/g/s/link-resolution?q={code}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.FromCode(response.json()["linkInfoV2"]).FromCode

    # ========== LINK FROM OBJECT ID ============

    def get_from_id(self, objectId: str, objectType: int = 0, comId: str = None):
        # Use json key ["linkInfoV2"] to get only (unknown)
        data = json.dumps({
            "objectId": objectId,
            "targetCode": 1,
            "objectType": objectType,
            "timestamp": int(timestamp() * 1000)
        })

        if comId:
            response = self.session.post(f"{self.api}/g/s-x{comId}/link-resolution", headers=self.headers(data=data),
                                         data=data)
        else:
            response = self.session.post(f"{self.api}/g/s/link-resolution", headers=self.headers(data=data), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.FromCode(response.json()["linkInfoV2"]).FromCode

    # ======= CLAIM NEW USER COUPON ==========

    def claim_new_user_coupon(self):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/g/s/coupon/new-user-coupon/claim", headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== GET SUBSCRIPTIONS ============

    def get_subscriptions(self, start: int = 0, size: int = 25):
        # Use json key ["storeSubscriptionItemList"] to get only subscription list
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/store/subscription?objectType=122&start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.json()["storeSubscriptionItemList"]

    # ============ GET ALL USERS ==============

    def get_all_users(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/g/s/user-profile?type=recent&start={start}&size={size}",
                                    headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(response.json()).UserProfileCountList

    # ============= ACCEPT HOST ==============

    def accept_host(self, chatId: str, requestId: str):
        #        data = json.dumps({})
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept",
                                         headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============= LINK IDENTITY ==============
    # by: https://github.com/LynxN1

    def link_identify(self, code: str):
        response = self.session.get(
            f"{self.api}/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}",
            headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ========= INVITE TO VOICE CHAT ============

    def invite_to_vc(self, chatId: str, userId: str):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({
                "uid": userId
            })

            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/vvchat-presenter/invite",
                                         headers=self.headers(data=data), data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ============ WALLET CONFIG ==============

    def wallet_config(self, level: int):
        #        Changes ads config

        #        **Parameters**
        #            - **level** - Level of the ads.
        #                - ``1``, ``2``

        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({
                "adsLevel": level,
                "timestamp": int(timestamp() * 1000)
            })

            response = self.session.post(f"{self.api}/g/s/wallet/ads/config", headers=self.headers(data=data),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # ========== GET AVATAR FRAMES ============

    def get_avatar_frames(self, start: int = 0, size: int = 25):
        # Use json key ["avatarFrameList"] to get only avatar frame list
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            response = self.session.get(f"{self.api}/g/s/avatar-frame?start={start}&size={size}",
                                        headers=self.headers())
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.AvatarFrameList(response.json()["avatarFrameList"]).AvatarFrameList

    # ======== UPLOAD BUBBLE PREVIEW ==========
    # By Romanok2805

    def upload_bubble_preview(self, file: BinaryIO) -> str:
        # Use json key ["mediaValue"] to get only image url
        #        Upload bubble preview image to the amino servers. Authorization required.
        #        **Parameters**
        #            - **file** : PNG image to be uploaded.
        #        **Returns**
        #            - **Success** : Url of the bubble preview image uploaded to the server.
        #            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`

        data = file.read()
        response = self.session.post(f"{self.api}/g/s/media/upload/target/chat-bubble-thumbnail",
                                     headers=self.headers(data=data, type="image/png"), data=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.json()["mediaValue"]

    # ========= CREATE BUBBLE CONFIG ===========
    # By Romanok2805

    def create_bubble_config(self, allowedSlots: list = None, contentInsets: list = None, coverImage: str = None, id: str = None, name: str = None, previewBackgroundUrl: str = None, slots: list = None, templateId: str = None, version: int = 1, vertexInset: int = 0, zoomPoint: list = None, backgroundPath: str = None, color: str = None, linkColor: str = None) -> objects.BubbleConfig:
        bubbleConfig = {
            "allowedSlots": allowedSlots or [{"align": 1, "x": 5, "y": -5}, {"align": 2, "x": -30, "y": -5}, {"align": 4, "x": -30, "y": 5}, {"align": 3, "x": 5, "y": 5}],
            "contentInsets": contentInsets or [26, 33, 18, 49],
            "coverImage": coverImage or "http://cb1.narvii.com/7991/fea4e00136e7c0cba79f3b1c0a130d20a12a5624r10-356-160_00.png",
            "id": id,
            "name": name or "Spring (Template)",
            "previewBackgroundUrl": previewBackgroundUrl or "http://cb1.narvii.com/images/6846/96234993898693503497b011ad56c95f028790fa_00.png",
            "slots": slots,
            "templateId": templateId or "949156e1-cc43-49f0-b9cf-3bbbb606ad6e",
            "version": version,
            "vertexInset": vertexInset,
            "zoomPoint": zoomPoint or [41, 44],
            "backgroundPath": backgroundPath or "background.png",
            "color": color or "#fff45e",
            "linkColor": linkColor or "#74ff32"
        }
        return objects.BubbleConfig(bubbleConfig).BubbleConfig

    # =========== GENERATE BUBBLE =============
    # By Romanok2805

    def generate_bubble(self, bubbleImage: BinaryIO = None, bubbleConfig: objects.BubbleConfig = None) -> BinaryIO:
        """
        Generate bubble file-like object (zip)
        **Parameters**
            - **bubbleImage** : PNG image of bubble
            - **bubbleConfig** : Config bubble
        **Returns**
            - **Success** : ZIP file-like object
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        if bubbleImage is None:
            with self.session.get(
                "http://cb1.narvii.com/images/6846/eebb8b22237e1b80f46de62284abd0c74cb440f9_00.png") as response: bubbleImage = io.BytesIO(
                response.content)

        if bubbleConfig is None: bubbleConfig = self.create_bubble_config()

        buffer = io.BytesIO()
        zipf = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)
        try:
            zipf.writestr(bubbleConfig.backgroundPath, data=bubbleImage.read())
            zipf.writestr("config.json", data=json.dumps(bubbleConfig.json))
        finally:
            zipf.close()
        buffer.seek(0)
        return buffer

    # ============= LOAD BUBBLE ================
    # By Romanok2805

    def load_bubble(self, bubble_zip: BinaryIO) -> Tuple[bytes, objects.Bubble]:
        """
        Load bubble from ZIP file-like object
        **Parameters**
            - **bubble_zip** : ZIP file-like bubble with bg and config
        **Returns**
            - **Success** : background bytes PNG and BubbleConfig
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        zipf = zipfile.ZipFile(bubble_zip, 'r')
        cfgTemp = json.loads(zipf.read("config.json"))
        print(cfgTemp)
        config = objects.BubbleConfig(cfgTemp).BubbleConfig
        background = zipf.read(config.backgroundPath)
        return background, config

    # ======= SUBSCRIBE TO AMINO PLUS =========

    def subscribe_amino_plus(self):
        if not self.authenticated:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()
        else:
            data = json.dumps({
                {
                    "sku": "d940cf4a-6cf2-4737-9f3d-655234a92ea5",
                    "packageName": "com.narvii.amino.master",
                    "paymentType": 1,
                    "paymentContext": {
                        "transactionId": str(uuid4()),
                        "isAutoRenew": True
                    },
                    "timestamp": timestamp()
                }
            })
            response = self.session.post(f"{self.api}/g/s/membership/product/subscribe", headers=self.headers(),
                                         data=data)
            if response.json()['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(response.json())
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.text

    # =========== GET VIDEO REP INFO ============
    # By SirLez & Bovonos

    def get_video_rep_info(self, chatId: str):
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}/avchat-reputation", headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.RepInfo(response.json()).RepInfo

    # ============ CLAIM VIDEO REP ==============
    # By SirLez & Bovonos

    def claim_video_rep(self, chatId: str):
        info = self.get_video_rep_info(chatId)
        reputation = info.json["reputation"]

        if int(reputation) < 1:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().cannotNotClaimReputation()
            else:
                raise exceptions.CannotNotClaimReputation()

        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/avchat-reputation", headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Rep(response.json()).Rep

    # ============= SEND ACTION ================

    def send_action(self, actions: list, comId: str, chatId: str = None, blogId: str = None, quizId: str = None, lastAction: bool = False):
        # Action List
        # Browsing

        if lastAction is True:
            t = 306
        else:
            t = 304

        data = {
            "o": {
                "actions": actions,
                "target": f"ndc://x{comId}/",
                "ndcId": int(comId),
                "params": {"topicIds": [45841, 17254, 26542, 42031, 22542, 16371, 6059, 41542, 15852]},
                "id": "273887"
            },
            "t": t
        }

        if blogId is not None or quizId is not None:
            data["o"]["target"] = f"ndc://x{comId}/blog/{blogId}"
            if blogId is not None: data["o"]["params"]["blogType"] = 0
            if quizId is not None: data["o"]["params"]["blogType"] = 6
        if chatId is not None:
            data["o"]["target"] = f"ndc://x{comId}/chat-thread/{chatId}"
            data["o"]["params"] = {"membershipStatus": 1, "threadType": 2}

        sleep(2)
        return self.send(json.dumps(data))

    def wssClient(self):
        return aminos.Wss(self.headers()).getClient()

# Hydrochloric.py - Kapidev#4448
# Customizabled by Oustex
# SAmino - https://github.com/SirLez/SAmino
# Amino.py - https://github.com/Slimakoi/Amino.py
# Amino-new.py https://github.com/aminobot22/MAmino.py
# Amino-Socket - https://github.com/Hanamixp/Amino-Socket
