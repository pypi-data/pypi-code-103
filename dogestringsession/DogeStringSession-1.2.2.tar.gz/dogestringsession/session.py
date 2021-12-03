# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from base64 import b64decode
from random import choice

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.network import ConnectionTcpAbridged
from telethon.sessions import StringSession

from . import *
from .keys import *
from .language import LAN

LAN = LAN["SESSION"]


def sessiongenerator():
    p_info(f"🤔 {LAN['IS_DOGE_RELIABLE']}!")
    while True:
        phonenumber = wowask(
            f"[bold white]⏩ {LAN['SAMPLE_NUMBER']}[/]\n\n[bold yellow]📲 {LAN['PHONE_NUMBER']}:[/]"
        )
        if phonenumber.startswith("+"):
            break
    p_info(f"⏳ {LAN['SESSION_GENERATING']}...")
    AI, AH = choice(((AI1, AH1), (AI2, AH2), (AI3, AH3)))
    AID = b64decode(AI)
    AHH = b64decode(AH)
    client = InteractiveTelegramClient(StringSession(), AID, AHH, phonenumber)
    return client.session.save(), client


class InteractiveTelegramClient(TelegramClient):
    def __init__(self, session_user_id, api_id, api_hash, phone=None, proxy=None):
        super().__init__(
            session_user_id,
            api_id,
            api_hash,
            connection=ConnectionTcpAbridged,
            proxy=proxy,
        )
        loop = get_event_loop()
        self.found_media = {}
        p_info(f"⏳ {LAN['CONNECTING']}...")
        try:
            loop.run_until_complete(self.connect())
        except IOError:
            p_error(f"[bold white]🔸 {LAN['RETRYING']}...[/]")
            loop.run_until_complete(self.connect())

        if not loop.run_until_complete(self.is_user_authorized()):
            if phone is None:
                while True:
                    user_phone = wowask(
                        f"[bold white]⏩ {LAN['SAMPLE_NUMBER']}[/]\n\n[bold yellow]📲 {LAN['PHONE_NUMBER']}:[/]"
                    )
                    if user_phone.startswith("+"):
                        break
            else:
                user_phone = phone
            try:
                loop.run_until_complete(self.sign_in(user_phone))
                self_user = None
            except (PhoneNumberInvalidError, ValueError):
                p_error(
                    f"[bold white]⏩ {LAN['SAMPLE_NUMBER']}[/]\n\n📲 {LAN['PHONE_NUMBER']}:"
                )
                exit(1)

            except FloodWaitError as e:
                p_error(
                    f"💤 {LAN['ERROR_FW'].format(e.seconds)}.\n\n🔁 {LAN['TRY_AGAIN_FW'].format(e.seconds)}!"
                )
                exit(1)

            while self_user is None:
                code = wowask(f"🔢 {LAN['WRITE_CODE_FROM_TG']}:")
                try:
                    self_user = loop.run_until_complete(self.sign_in(code=code))
                except PhoneCodeInvalidError:
                    p_error(
                        f"🔸 {LAN['INVALID_CODE']}!\n\n📍 {LAN['TRY_AGAIN']}.\n\n[{LAN['WARNING']}.]:"
                    )
                except PhoneCodeExpiredError:
                    p_error(f"🤨 {LAN['EXPIRED']}.")
                    exit(1)

                except FloodWaitError as e:
                    p_error(
                        f"💤 {LAN['ERROR_FW'].format(e.seconds)}.\n\n🔁 {LAN['TRY_AGAIN_FW'].format(e.seconds)}!"
                    )
                    exit(1)

                except SessionPasswordNeededError:
                    pw = wowask(f"🔐 {LAN['PASS']}:")
                    try:
                        self_user = loop.run_until_complete(self.sign_in(password=pw))
                    except PasswordHashInvalidError:
                        p_error(
                            f"🔸 {LAN['INVALID_2FA']}!\n\n📍 {LAN['TRY_AGAIN']}.\n\n[{LAN['WARNING']}.]:"
                        )
                    except FloodWaitError as e:
                        p_error(
                            f"💤 {LAN['ERROR_FW'].format(e.seconds)}.\n\n🔁 {LAN['TRY_AGAIN_FW'].format(e.seconds)}!"
                        )
                        exit(1)
