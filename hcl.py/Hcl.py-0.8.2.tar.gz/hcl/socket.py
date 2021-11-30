import base64
import hmac
import time
import json
from hashlib import sha1

import requests
import websocket
import threading
import contextlib
import ssl
from random import randint

from sys import _getframe as getframe
from .src import objects, debugs

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

# ============ SOCKET BELOW ============

#              Please, do not change anything 
#      below, else your library probably will stop
#                                   working.

class SocketHandler:
    def colored(self, r, g, b, text, rb : int = None, gb : int = None, bb : int = None):
    # print(colored(200, 20, 200, 0, 0, 0, "Hello World"))
        if rb is None and gb is None and bb is None:
            return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)
        else:
            return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m{}\033[0m".format(r, g, b, rb, gb, bb, text)

    def __init__(self, client, socket_trace = False, socket_debug = False, security = True):
        self.socket_url = "wss://ws1.narvii.com"
        self.client = client
        if debugs.enabled == True:
            socket_debug = True
        self.socket_debug = socket_debug
        self.active = False
        self.socket_headers = None
        self.security = security
        self.socket = None
        self.socket_thread = None
        self.reconnect = True
        self.socket_stop = False
        self.socketDelay = 0
        self.minReconnect = 480
        self.maxReconnect = 540
        self.asWeb = False

        self.socket_handler = threading.Thread(target = self.reconnect_handler)
        self.socket_handler.start()

        websocket.enableTrace(socket_trace)

    @staticmethod
    def signature(data) -> str:
        mac = hmac.new(bytes.fromhex("307c3c8cd389e69dc298d951341f88419a8377f4"), data.encode("utf-8"), sha1)
        digest = bytes.fromhex("22") + mac.digest()
        return base64.b64encode(digest).decode("utf-8")

    def reconnect_handler(self):
        # Made by enchart#3410 thx
        # Fixed by The_Phoenix#3967
        while True:
            temp = randint(self.minReconnect, self.maxReconnect)
            time.sleep(temp)

            if self.active:
                if self.socket_debug is True:
                    print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" RECONNECT HANDLER ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Random refresh time = {temp} seconds, Reconnecting Socket "))
                self.close()
                self.start_socket(self.asWeb)

    def on_open(self):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" ON OPEN ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Socket Opened "))

    def on_close(self):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" ON CLOSE ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Socket Closed "))

        #self.active = False

        if self.reconnect:
            if self.socket_debug is True:
                print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" ON CLOSE ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Reconnect is True, Opening Socket "))

            self.start_socket(self.asWeb)

    def on_ping(self, data):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" ON PING ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Socket Pinged "))

        contextlib.suppress(self.socket.sock.pong(data))

    def handle_message(self, data):
        self.client.handle_socket_message(data)
        return

    def send(self, data):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" SEND ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Sending Data "))
            print(self.colored(186, 165, 234, rb=36, gb=36, bb=36, text=f" {data}"))

        self.socket.send(data)

    def token(self):
        head = {
            "cookie": f"sid={self.client.sid()}"
        }
        response = requests.get("https://aminoapps.com/api/chat/web-socket-url", headers=head)
        if response.status_code != 200: return response.text
        else: return json.loads(response.text)["result"]["url"]

    def start_socket(self, asWeb: bool = False):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" START ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Starting Socket "))

        if self.client.sid is None:
            if self.socket_debug is True:
                print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" START ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" client.sid is None "))

            return

        final = f"{self.client.deviceId()}|{int(time.time() * 1000)}"

        if asWeb is True:
            if self.socket_debug is True:
                print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" START ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Using WebSocket via Web "))

            websocketUrl = self.token()

            self.socket_headers = {
                "cookie": f"sid={self.client.sid()}"
            }

            self.asWeb = True
        else:
            if self.socket_debug is True:
                print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" START ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Using WebSocket via App "))

            websocketUrl = f"{self.socket_url}/?signbody={final.replace('|', '%7C')}"

            self.socket_headers = {
                "NDCDEVICEID": self.client.deviceId(),
                "NDCAUTH": f"sid={self.client.sid()}",
                "NDC-MSG-SIG": self.signature(final)
            }

            self.asWeb = False

        self.socket = websocket.WebSocketApp(
            websocketUrl,
            on_message = self.handle_message,
            on_open = self.on_open,
            on_close = self.on_close,
            on_ping = self.on_ping,
            header = self.socket_headers
        )

        socket_settings = {
            "ping_interval": 60
        }

        if not self.security:
            socket_settings.update({
                'sslopt': {
                    "cert_reqs": ssl.CERT_NONE,
                    "check_hostname": False
                }
            })

        self.socket_thread = threading.Thread(target = self.socket.run_forever, kwargs = socket_settings)
        self.socket_thread.start()
        self.active = True

        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" START ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Socket Started "))

    def close(self):
        if self.socket_debug is True:
            print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" CLOSE ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Closing Socket "))

        self.reconnect = False
        self.active = False
        self.socket_stop = True
        try:
            self.socket.close()
        except Exception as closeError:
            if self.socket_debug is True:
                print(self.colored(255, 255, 255, rb=154, gb=0, bb=243, text=" SOCKET ❯ ") + self.colored(255, 255, 255, rb=119, gb=0, bb=186, text=" CLOSE ❯ ") + self.colored(255, 255, 255, rb=83, gb=0, bb=133, text=f" Error while closing Socket "))
                print(self.colored(186, 165, 234, rb=36, gb=36, bb=36, text=f" {closeError}"))

        return


class Callbacks:
    def __init__(self, client):
        self.client = client
        self.handlers = {}

        self.methods = {
            10: self._resolve_payload,
            304: self._resolve_chat_action_start,
            306: self._resolve_chat_action_end,
            1000: self._resolve_chat_message
        }

        self.chat_methods = {
            "0:0": self.on_text_message,
            "0:100": self.on_image_message,
            "0:103": self.on_youtube_message,
            "1:0": self.on_strike_message,
            "2:110": self.on_voice_message,
            "3:113": self.on_sticker_message,
            "52:0": self.on_voice_chat_not_answered,
            "53:0": self.on_voice_chat_not_cancelled,
            "54:0": self.on_voice_chat_not_declined,
            "55:0": self.on_video_chat_not_answered,
            "56:0": self.on_video_chat_not_cancelled,
            "57:0": self.on_video_chat_not_declined,
            "58:0": self.on_avatar_chat_not_answered,
            "59:0": self.on_avatar_chat_not_cancelled,
            "60:0": self.on_avatar_chat_not_declined,
            "100:0": self.on_delete_message,
            "101:0": self.on_group_member_join,
            "102:0": self.on_group_member_leave,
            "103:0": self.on_chat_start,
            "104:0": self.on_chat_background_changed,
            "105:0": self.on_chat_title_changed,
            "106:0": self.on_chat_icon_changed,
            "107:0": self.on_voice_chat_start,
            "108:0": self.on_video_chat_start,
            "109:0": self.on_avatar_chat_start,
            "110:0": self.on_voice_chat_end,
            "111:0": self.on_video_chat_end,
            "112:0": self.on_avatar_chat_end,
            "113:0": self.on_chat_content_changed,
            "114:0": self.on_screen_room_start,
            "115:0": self.on_screen_room_end,
            "116:0": self.on_chat_host_transfered,
            "117:0": self.on_text_message_force_removed,
            "118:0": self.on_chat_removed_message,
            "119:0": self.on_text_message_removed_by_admin,
            "120:0": self.on_chat_tip,
            "121:0": self.on_chat_pin_announcement,
            "122:0": self.on_voice_chat_permission_open_to_everyone,
            "123:0": self.on_voice_chat_permission_invited_and_requested,
            "124:0": self.on_voice_chat_permission_invite_only,
            "125:0": self.on_chat_view_only_enabled,
            "126:0": self.on_chat_view_only_disabled,
            "127:0": self.on_chat_unpin_announcement,
            "128:0": self.on_chat_tipping_enabled,
            "129:0": self.on_chat_tipping_disabled,
            "65281:0": self.on_timestamp_message,
            "65282:0": self.on_welcome_message,
            "65283:0": self.on_invite_message
        }

        self.notif_methods = {
            "53": self.on_set_you_host,
            "67": self.on_set_you_cohost,
            "68": self.on_remove_you_cohost
        }

        self.chat_actions_start = {
            "Typing": self.on_user_typing_start,
        }

        self.chat_actions_end = {
            "Typing": self.on_user_typing_end,
        }

    def _resolve_payload(self, data):
        key = f"{data['o']['payload']['notifType']}"
        return self.notif_methods.get(key, self.default)(data)

    def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
        return self.chat_methods.get(key, self.default)(data)

    def _resolve_chat_action_start(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_start.get(key, self.default)(data)

    def _resolve_chat_action_end(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_end.get(key, self.default)(data)

    def resolve(self, data):
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(data)

    def event(self, type):
        def registerHandler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler

        return registerHandler

    def on_set_you_host(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event.payload)
    def on_remove_you_cohost(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event.payload)
    def on_set_you_cohost(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event.payload)

    def on_text_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_image_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_youtube_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_strike_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_sticker_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_delete_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_group_member_join(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_group_member_leave(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_background_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_title_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_icon_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_content_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_screen_room_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_screen_room_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_host_transfered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_text_message_force_removed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_removed_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_text_message_removed_by_admin(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tip(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_pin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_open_to_everyone(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_invited_and_requested(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_invite_only(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_view_only_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_view_only_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_unpin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tipping_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tipping_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_timestamp_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_welcome_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_invite_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)

    def on_user_typing_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_user_typing_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)

    def default(self, data): self.call(getframe(0).f_code.co_name, data)
