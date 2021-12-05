# -*- coding: utf-8 -*-
import scrapy
import requests
from fake_useragent import UserAgent
from rommon.Citybrain_Spider.items import CitybrainSpiderItem
import logging
import csv

from rommon.Citybrain_Spider.utils import util

logger = logging.getLogger(__name__)

ua = UserAgent()


class CitySpSpider(scrapy.Spider):
    name = 'city_sp'

    def __init__(self, allowed_domains=None, start_urls=None, res=None, name=None, description=None,
                 category=None, link_url=None, next_page=None, last_page=None, *args, **kwargs):
        super(CitySpSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [allowed_domains]
        self.start_urls = [start_urls]
        self.res = res
        self.name = name
        self.description = description
        self.category = category
        self.link_url = link_url
        self.next_page = next_page
        self.last_page = last_page

    def parse(self, response):
        results = response.xpath(f'{self.res}')
        for i in results:
            Name = i.xpath(f'{self.name}/text()').extract_first()
            Descriptions = i.xpath(f'{self.description}//text()').extract()
            j = ""
            try:
                for nn in Descriptions:
                    if "http" not in nn:
                        if "www" not in nn:
                            j = j + nn
                Description = j
                # print("success："+Description)
            except:
                Description = i.xpath(f'{self.description}/b/text()').extract_first()
                # print("fail："+Description)
            # 获取详情API
            Link_url = i.xpath(f'{self.link_url}/@href').extract_first()
            # 切片截取
            ye = Link_url.split('/')[-1]
            yuming = self.allowed_domains[0]
            # API详情
            json_url = f'https://{yuming}/api/views/{ye}.json'
            api_res = self.parse_url(json_url)
            Tags = api_res[0]
            Dataset_Owner = api_res[1]
            Source_Link = api_res[2]
            Category = api_res[3]

            # 获取rows
            rows_url = f'https://{yuming}/api/id/{ye}.json?$select=count(*)%20as%20__count_alias__'
            api_rows = self.select_rows(rows_url)
            Rows = api_rows

            item = CitybrainSpiderItem()
            item['Name'] = Name
            item['Description'] = Description
            item['Link_url'] = Link_url
            item['Tags'] = Tags
            item["Rows"] = Rows
            item['Dataset_Owner'] = Dataset_Owner
            item['Source_Link'] = Source_Link
            item['Category'] = Category
            logger.info(item)
            util.save_results(item)
            yield item

        # print(data_list)
        # 下一页
        next_url = response.xpath(f'{self.next_page}/@href').extract_first()

        # 判断最后一页
        last_url = response.xpath(f'{self.last_page}/@class').extract_first()
        # print(last_url)
        if last_url in "end lastLink browse2-pagination-button pagination-button":
            yuming = self.allowed_domains[0]
            sss = f'https://{yuming}/{next_url}'
            print(sss)
            yield scrapy.Request(
                sss,
                callback=self.parse
            )

    def parse_url(self, url):
        url = url
        headers = {"User-Agent": ua.random}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        res_list = res.json()
        yuming = self.allowed_domains[0]
        print(yuming + "网站：" + res_list["name"])
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
