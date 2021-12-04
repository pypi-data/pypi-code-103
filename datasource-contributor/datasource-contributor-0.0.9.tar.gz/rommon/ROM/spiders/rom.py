# -*- coding: utf-8 -*-
import scrapy
import requests
from lxml import etree
from fake_useragent import UserAgent
from rommon.ROM.items import RomItem

ua = UserAgent()


class RomSpider(scrapy.Spider):
    name = 'rom'
    allowed_domains = ['controllerdata.lacity.org']
    # start_urls = ['https://controllerdata.lacity.org/browse?&page=1']
    start_urls = ['https://controllerdata.lacity.org/browse?limitTo=datasets&page=1']

    # start_urls01 = ['https://controllerdata.lacity.org/browse?&page=1']

    def parse(self, response):
        data_list = []
        results = response.xpath('//*[@class="browse2-results"]/div')
        for i in results:
            Name = i.xpath('.//h2/a/text()').extract_first()
            Description = i.xpath('./div/div[2]/div[1]/div/div[1]/div[1]/text()').extract_first()
            # 获取详情API
            Link_url = i.xpath('.//h2/a/@href').extract_first()
            # 切片截取
            ye = Link_url.split('/')[-1]
            # API详情
            json_url = 'https://controllerdata.lacity.org/api/views/' + ye + '.json'
            api_res = self.parse_url(json_url)
            Tags = api_res[0]
            Dataset_Owner = api_res[1]
            Source_Link = api_res[2]
            Category = api_res[3]
            # 获取rows
            rows_url = "https://controllerdata.lacity.org/api/id/" + ye + ".json?$select=count(*)%20as%20__count_alias__"
            api_rows = self.select_rows(rows_url)
            Rows = api_rows

            # data_d={
            #     "name":name,
            #     "content":content,
            #     "url":url,
            #     "downloads":down,
            #     "tag":tag
            # }
            # print(data_d)
            # data_list.append(data_d)
            item = RomItem()
            item['Name'] = Name
            item['Description'] = Description
            item['Link_url'] = Link_url
            item["Rows"] = Rows
            item['Tags'] = Tags
            item['Dataset_Owner'] = Dataset_Owner
            item['Source_Link'] = Source_Link
            item['Category'] = Category
            yield item

        # print(data_list)
        # 下一页
        next_url = response.xpath(
            '//*[@class="next nextLink browse2-pagination-button pagination-button"]/@href').extract_first()

        # 判断最后一页
        last_url = response.xpath('//*[@class="pagination"]/a[last()]/@class').extract_first()
        # print(last_url)
        if last_url in "end lastLink browse2-pagination-button pagination-button":
            sss = "https://controllerdata.lacity.org/" + next_url
            # print(sss)
            yield scrapy.Request(
                sss,
                callback=self.parse
            )

        return data_list

    # def parse_xiangqing(self,url):
    #     ua = UserAgent()
    #     # 新房请求的网址
    #     url = url
    #     # 请求头
    #     # ua.random  随机生成user_agent
    #     headers = {"User-Agent": ua.random}
    #     # 请求
    #     response = requests.get(url=url, headers=headers)
    #     # 手动指定字符编码格式，常用有"utf-8"\"gbk"
    #     response.encoding = "gbk"
    #     # 响应体内容
    #     dddd = response.text
    #     xiangqing = etree.HTML(dddd)
    #
    #     downloads=xiangqing.xpath('//*[@class="metadata-pair download-count"]/dd/text()')
    #     return downloads

    def parse_url(self, url):
        url = url
        headers = {"User-Agent": ua.random}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        res_list = res.json()
        print("controllerdat网站：" + res_list["name"])
        dataset_owner = res_list["tableAuthor"]["displayName"]

        try:
            if True:
                tags = res_list["tags"]
        except:
            tags = None

        try:
            if True:
                Source_Link = res_list["attributionLink"]
        except:
            Source_Link = None

        try:
            if True:
                category = res_list["category"]
        except:
            category = None

        return tags, dataset_owner, Source_Link, category

    def select_rows(self, url):
        url = url
        headers = {"User-Agent": ua.random}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        res_rows = res.json()
        for k in res_rows[0]:
            rows = res_rows[0][k]
            return rows
