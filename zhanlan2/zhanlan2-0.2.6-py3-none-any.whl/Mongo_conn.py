#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 17:46
# @Author  : Adyan
# @File    : Mongo_conn.py
from datetime import datetime

from pymongo import MongoClient


class MongoConn(object):
    def __init__(self, db_name, config):
        """
        :param db_name:
        :param config: {
            "host": "192.168.20.211",
            # "host": "47.107.86.234",
            "port": 27017
            }
        """
        self.db = MongoClient(**config, connect=True)[db_name]


class DBBase(object):

    def __init__(self, collection, db_name, config):
        self.mg = MongoConn(db_name, config)
        self.collection = self.mg.db[collection]

    def exist_list(self, data, key, get_id: callable):

        lst = [get_id(obj) for obj in data]
        print('lst', len(lst))
        set_list = set([
            i.get(key)
            for i in list(
                self.collection.find({key: {"$in": lst}})
            )
        ])
        set_li = set(lst) - set_list
        with open("./ignore/null_field.txt", "rt", encoding="utf-8") as f:
            _ignore = [int(line.split(",")[0]) for line in f.readlines()]
        exist = list(set_li - set(_ignore))
        print(len(exist))
        for obj in data:
            if get_id(obj) in exist:
                yield obj

    def exist(self, dic):
        """
        单条查询
        :param dic:
        :return:1,0
        """
        return self.collection.find(dic).count()

    def update_one(self, dic, item=None):
        result = self.exist(dic)
        if item and result == 1:
            item['updateTime'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            self.collection.update(dic, {"$set": item})
        elif item:
            self.collection.update(dic, {"$set": item}, upsert=True)

    def insert_one(self, param):
        """
        :param param: 多条list 或者 单条dict
        :return:
        """
        self.collection.insert(param)

    def find_len(self, dic):
        return self.collection.find(dic).count()

    def find_one(self):
        return self.collection.find_one()

    def find_list(self, count, dic=None, page=None, ):
        """
        查询数据
        :param count:查询量
        :param dic:{'city': ''} 条件查询
        :param page:分页查询
        :return:
        """
        if dic:
            return list(self.collection.find(dic).limit(count))
        if page:
            return list(self.collection.find().skip(page * count - count).limit(count))

    def daochu(self):
        return list(self.collection.find({'$and': [
            {'$or': [{"transaction_medal": "A"}, {"transaction_medal": "AA"}]},
            {"tpServiceYear": {'$lte': 2}},
            {"overdue": {'$ne': "店铺已过期"}},
            {"province": "广东"}
        ]}))

    # return self.collection.find().skip(count).next()
    def test(self):
        return self.collection


class MongoPerson(DBBase):
    def __init__(self, table, db_name, config):
        super(MongoPerson, self).__init__(table, db_name, config)
