
import pymysql
from datetime import datetime
from pymysql.err import IntegrityError
import logging
from pymysql import cursors
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
import json

class MySQLPipeline:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spide):
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = item
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (item.table, keys, values)
        try:
            self.db.ping(reconnect=True)
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
            logging.debug('Crawl done.' )
        except IntegrityError:
            self.db.rollback()
            logging.info('去重 Skip .') 
        return item