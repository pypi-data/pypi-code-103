# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import os





class RomPipeline(object):
    # fp= None
    #只会在爬虫启动的时候执行，只执行一次
    def open_spider(self,spider): #必须要加spider
        print("开始爬取---")
        self.fp=open('row.csv', 'w', encoding='utf-8', newline='')
        self.writer = csv.writer(self.fp)
        self.writer.writerow(["name", "content", "url","downloads","tag"])

    def process_item(self, item, spider):
        name=item['name']
        content=item['content']
        url=item['url']
        downloads=item['downloads']
        tag=item['tag']
        #
        # # self.fp.write(name + "," + str(content) +","+url+","+str(downloads)+","+str(tag)+ "\n")
        ase=[name,content,url,downloads,tag]
        row = [ase]
        for r in row:
            self.writer.writerow(r)
        return item

    #结束的时候执行一次
    def close_spider(self,spider):
        print("爬取结束！")
        self.fp.close()