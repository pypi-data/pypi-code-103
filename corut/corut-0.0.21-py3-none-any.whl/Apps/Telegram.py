#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It sends information such as message, video, picture via telegram.
It doesn't work like a bot, login with normal user information.

In order to avoid problems when working under multiprocessing or QT,
it is run by running a separate file during separate submission.

Get ID via link ---> https://my.telegram.org/apps
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import sys
from ..Apps.FileRw import file_rw
from ..Decorators import try_except
from ..OS import join_directory, delete_files_or_folders, get_path_temp
from ..Shell import run_cmd
from telethon.sync import TelegramClient


SENDER_ON_THREAD = """
FROM_NUMBER = '{}'
API_ID = {}
API_HASH = '{}'
TO_LIST = {}
ATTACHMENTS = {}


try:
    import os
    from telethon import TelegramClient
    client = TelegramClient(FROM_NUMBER, API_ID, API_HASH)
except Exception as e:
    client = None
    print('#############>TELEGRAM ERROR:#%s#' % e)


async def message_sender(to, text, attachments):
    try:
        await client.send_message(to, text)
        if attachments is not None:
            for file_path in (attachments if isinstance(attachments, list) else [attachments]):
                if os.path.exists(file_path):
                    file = await client.upload_file(file_path)
                    await client.send_file(to, file)
                else:
                    print('###> TELEGRAM SEND FILE ERROR! --> %s invalid extension...' % file_path)
        await client.disconnect()
        print('********* TELEGRAM SEND SUCCESS *********> TO:##%s##' % to)
    except Exception as error:
        print('#############>TELEGRAM ERROR:#%s#' % error)
    return 0


def starter(to, text, attachments):
    try:
        with client:
            client.loop.run_until_complete(message_sender(to, text, attachments))
    except Exception as error:
        print('#############>TELEGRAM ERROR:#%s#' % error)


if client is not None:
    for user in TO_LIST:
        if user is not None:
            starter(user, TEXT, ATTACHMENTS)
            print(
                'Your message sent from %s to %s via Telegram has been transmitted:'
                '##%s## Attachments:%s' % (FROM_NUMBER, user, TEXT, ATTACHMENTS)
            )
"""


class Telegram:
    def __init__(self):
        self.api_id = 0
        self.api_hash = None
        self.from_number = None
        self.authentication_id = None
        self.__session = None

    @try_except
    def connect(self):
        print(self.from_number, self.api_id, self.api_hash, self.authentication_id)
        self.__session = TelegramClient(self.from_number, self.api_id, self.api_hash)
        self.__session.connect()

    @try_except
    def disconnect(self):
        if self.__session:
            self.__session.disconnect()

    @try_except
    def create_authentication_for_session(self):
        if not self.__session.is_user_authorized():
            self.__session.send_code_request(self.from_number)
            self.__session.sign_in(self.from_number, self.authentication_id)

    @try_except
    def send_code_request(self):
        if self.__session:
            self.__session.send_code_request(self.from_number)

    def sign_in_after_send_code_request(self):
        sign = False
        try:
            self.__session.sign_in(self.from_number, self.authentication_id)
            sign = True
        except Exception as error:
            print(f'#############>TELEGRAM SING IN ERROR:#{error}#')
            sign = False
        finally:
            return sign

    @try_except
    def send_message(self, to_list, message, attachments=None):
        sender_file_path = join_directory(get_path_temp(), "Telegram_Sender.py")
        file_rw(
            path=sender_file_path,
            data=f'TEXT = """\n{message}\n"""' +
                 str(SENDER_ON_THREAD).format(
                     self.from_number,
                     self.api_id,
                     self.api_hash,
                     (to_list if isinstance(to_list, list) else [to_list]),
                     (
                         attachments if isinstance(attachments, list) else [attachments]
                         if attachments is not None else attachments
                     )
                 ),
            mode='w'
        )
        run_cmd(f'{sys.executable} {sender_file_path}')
        delete_files_or_folders(sender_file_path)
