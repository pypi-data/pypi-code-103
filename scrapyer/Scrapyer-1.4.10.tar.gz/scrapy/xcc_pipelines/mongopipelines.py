"""
date:2021/10/26
auth:t.y.jie
"""

import pymongo
from pymongo import MongoClient
class mongodbPipeline(object):
    def __init__(self,MONGO_HOST,MONGO_PORT,MONGO_PSW,MONGO_USER,MONGO_DB):
        # 链接数据库
        # self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        # # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(MINGO_USER, MONGO_PSW)
        mongo_url = 'mongodb://{0}:{1}@{2}:{3}/?authSource={4}&authMechanism=SCRAM-SHA-1'.format(MONGO_USER, MONGO_PSW,
                                                                                                 MONGO_HOST,MONGO_PORT, MONGO_DB)
        print('mongo_url',mongo_url)
        self.client = MongoClient(mongo_url)
        self.db = self.client[MONGO_DB]  # 获得数据库的句柄
        # self.coll = self.db[MONGO_COLL]  # 获得collection的句柄`

    @classmethod
    def from_crawler(cls, crawler):
        return cls(MONGO_HOST=crawler.settings.get('MONGO_HOST'),
                   MONGO_PORT=crawler.settings.get('MONGO_PORT'), 
                   MONGO_PSW=crawler.settings.get('MONGO_PSW'),
                   MONGO_USER=crawler.settings.get('MONGO_USER'),
                   MONGO_DB=crawler.settings.get('MONGO_DB'),
                   # MONGO_COLL=crawler.settings.get('MONGO_COLL'),
                   )

    def process_item(self, item, spider):
        try:
            postItem = dict(item)  # 把item转化成字典形式
            coll = self.db[item.table]
            coll.insert(postItem)  # 向数据库插入一条记录
        except pymongo.errors.DuplicateKeyError:
            print("去重了...",item)
        return item

    def close_spider(self):
        self.client.close()
