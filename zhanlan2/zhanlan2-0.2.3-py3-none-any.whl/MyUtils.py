#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/29 19:09
# @Author  : Adyan
# @File    : MyUtils.py

import json
import re
import time
import pytz
import random

from datetime import datetime
from faker import Faker

from .Mongo_conn import MongoPerson

fake = Faker()
cntz = pytz.timezone("Asia/Shanghai")


class ReDict:

    @classmethod
    def string(
            cls,
            re_pattern: dict,
            string_: str,
    ):
        if string_:
            return {
                key: cls.compute_res(
                    re_pattern=re.compile(scale),
                    string_=string_.translate(
                        {
                            ord('\t'): '', ord('\f'): '',
                            ord('\r'): '', ord('\n'): '',
                            ord(' '): '',
                        })
                )
                for key, scale in re_pattern.items()
            }

    @classmethod
    def compute_res(
            cls,
            re_pattern: re,
            string_=None
    ):
        data = [
            result.groups()[0]
            for result in re_pattern.finditer(string_)
        ]
        if data:
            try:
                return json.loads(data[0])
            except:
                return data[0]
        else:
            return None


class GoodsCopyUtils:

    @classmethod
    def time_cycle(
            cls,
            times,
            int_time=None
    ):
        """
        入库时间规整
        :param times: string - 字符串时间
        :param int_time: True and False  - 获时间戳
        :return:
        """
        if int_time:
            return int(time.mktime(time.strptime(times, "%Y-%m-%d")))
        if type(times) is str:
            times = int(time.mktime(time.strptime(times, "%Y-%m-%d %H:%M:%S")))
        return str(datetime.fromtimestamp(times, tz=cntz))

    @classmethod
    def merge_dic(
            cls,
            dic: dict,
            lst: list
    ):
        """
        合并多个dict
        :param dic: dict - 主dict
        :param lst: list - 多个字典列表方式传入
        :return:
        """
        for d in lst:
            for k, v in d.items():
                if v:
                    dic[k] = v
        return dic

    @classmethod
    def is_None(
            cls,
            dic: dict,
    ) -> dict:
        """
        :param dic: dict
        :return: 返回字典中值是None的键值对
        """
        return {
            k: v
            for k, v in dic.items()
            if not v
        }

    @classmethod
    def find(
            cls, target: str,
            dictData: dict,
    ) -> list:
        queue = [dictData]
        result = []
        while len(queue) > 0:
            data = queue.pop()
            for key, value in data.items():
                if key == target:
                    result.append(value)
                elif isinstance(value, dict):
                    queue.append(value)
        if result:
            return result[0]


class Headers:

    def headers(self, referer=None):
        while True:
            user_agent = fake.chrome(
                version_from=63, version_to=80, build_from=999, build_to=3500
            )
            if "Android" in user_agent or "CriOS" in user_agent:
                continue
            else:
                break
        if referer:
            return {
                "user-agent": user_agent,
                "referer": referer,
            }
        return {
            "user-agent": user_agent,
        }


class Cookies(object):

    def __init__(self, db_name, mongo_config):
        self.mongo_conn = MongoPerson(db_name, 'cookie', mongo_config).test()

    def cookie(self):
        return random.choice(list(self.mongo_conn.find()))


class SKU:
    def skuMap(self, param):
        data = [
            self.style(i.get("data_value"), i.get("skuName"), i.get("style"), i.get("cls"))
            for i in param
            if i.get("data_value")
        ]
        return self.sku(data), [s[1] for s in data]

    def style(self, data_value, skuName, style, cls):
        try:
            pid = data_value[0].split(":")[0]
        except:
            pid = None

        if style:
            styles = []
            for k, v in zip(
                    [
                        {'data_value': k, 'skuName': f'{cls[0]}--{v}'}
                        for k, v in zip(data_value, skuName)
                    ], style
            ):
                k.update({"image": v.replace("background:url(", '').replace(") center no-repeat;", '')})
                styles.append(k)
            props = {
                "values": [
                    {
                        'vid': k.split(":")[1],
                        'name': v,
                        'image': self.props_image(styles, k)
                    }
                    for k, v in zip(data_value, skuName)
                ],
                "name": cls[0],
                "pid": pid,
            }

        else:
            styles = [
                {'data_value': k, 'skuName': f'{cls[0]}--{v}'}
                for k, v in zip(data_value, skuName)
            ]
            props = {
                "values": [
                    {
                        'vid': k.split(":")[1],
                        'name': v,
                        'image': self.props_image(styles, k)
                    }
                    for k, v in zip(data_value, skuName)
                ],
                "name": cls[0],
                "pid": pid,
            }
        if pid:
            return styles, props
        else:
            return styles, None

    def sku(self, lis):
        results = []
        for data in lis:
            p1 = data[1]["values"]
            p2 = []
            for i, s in enumerate(data[0]):
                s.update({"image": p1[i]["image"]})
                p2.append(s)
            results.append(p2)

        shape = [len(v) for v in results]
        offsets = [0] * len(shape)
        has_next = True
        values = []

        while has_next:
            record = [results[i][off] for i, off in enumerate(offsets)]
            if not record:
                break
            res = self.format_data(record)
            values.append(res)

            for i in range(len(shape) - 1, -1, -1):
                if offsets[i] + 1 >= shape[i]:
                    offsets[i] = 0  # 重置并进位
                    if i == 0:
                        has_next = False  # 全部占满，退出
                else:
                    offsets[i] += 1
                    break

        return values

    def format_data(self, ls, ):
        p1 = []
        p2 = []
        p3 = []

        for li in ls:
            p1.append(list(li.values())[0])
            p2.append(list(li.values())[1])
            p3.append(list(li.values())[2])

        date_value = f";{';'.join(p1)};"
        skuName = f";{';'.join(p2)};"
        image = [i for i in p3 if i]

        return {"data_value": date_value, "skuName": skuName, "image": image[0] if image else None}

    def props_image(self, style, k):
        image = [
            i.get('image')
            for i in style
            if i.get('data_value') == k
        ]
        if image:
            return image[0]
