# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import time
import logging
from rommon.Citybrain_Spider.utils import util

logger = logging.getLogger(__name__)
a = int(time.time())
print("爬虫开始---")


class CitybrainSpiderPipeline(object):
    # fp= None
    # 只会在爬虫启动的时候执行，只执行一次
    def open_spider(self, spider):  # 必须要加spider
        print("01开始爬取---")
        # self.fp = open(f'../Citybrain_Spider/report/city_{a}.csv', 'w', encoding='utf-8', newline='')
        # self.writer = csv.writer(self.fp)
        # self.writer.writerow(
        #     ["Name", "Description", "Category", "Link_url", "Rows", "Tags", "Owner", "Source_Link", "Licence"])

    def process_item(self, item, spider):
        if spider.name == "city_sp":
            # if item['come_from']=="controllerdata":
            name = item['Name']
            description = item['Description']
            Link_url = item['Link_url']
            tags = item['Tags']
            rows = item["Rows"]
            dataset_owner = item['Dataset_Owner']
            source_link = item['Source_Link']
            category = item["Category"]

            # # self.fp.write(name + "," + str(content) +","+url+","+str(downloads)+","+str(tag)+ "\n")
            ase = [name, description, category, Link_url, rows, tags, dataset_owner, source_link]
            print(ase)
            row = [ase]
            for r in row:
                # 调接口 TODO
                print("row: %s" % r)
                util.save_results(r)
                # self.writer.writerow(r)
        return item

    # 结束的时候执行一次
    def close_spider(self, spider):
        print("01爬取结束！")
        # self.fp.close()
