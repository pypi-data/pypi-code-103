from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import reduce
from typing import List, Union

import requests
from bs4 import BeautifulSoup

from kabutobashi.errors import KabutobashiPageError

from .user_agent import UserAgent


@dataclass(frozen=True)
class PageDecoder:
    tag1: str = None
    class1: str = None
    id1: str = None
    default: str = ""

    def _decode(self, value):
        class1 = {"class": self.class1}

        set_value = None
        # tag1から取得
        if self.tag1 is not None:
            if class1["class"] is not None:
                set_value = value.find(self.tag1, self.class1)
            else:
                set_value = value.find(self.tag1)

        if set_value is None:
            return self.default

        # 文字列を置換して保持
        return self.replace(set_value.get_text())

    def decode(self, bs: BeautifulSoup) -> Union[str, List[str]]:
        return self._decode(value=bs)

    @staticmethod
    def replace(input_text: str) -> str:
        target_list = [" ", "\t", "\n", "\r", "円"]

        def remove_of(_input: str, target: str):
            return _input.replace(target, "")

        result = reduce(remove_of, target_list, input_text)
        return result.replace("\xa0", " ")


@dataclass(frozen=True)
class Page(metaclass=ABCMeta):
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _get(self) -> dict:
        raise NotImplementedError()

    def get(self) -> dict:
        data = self._get()
        data.update({"crawl_datetime": self.crawl_datetime()})
        return data

    @staticmethod
    def get_url_text(url: str) -> str:
        """
        requestsを使って、webからページを取得し、htmlを返す
        """
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return r.text

    @staticmethod
    def crawl_datetime() -> str:
        jst = timezone(timedelta(hours=+9), "JST")
        now = datetime.now(jst)
        return now.strftime("%Y-%m-%dT%H:%M:%S")
