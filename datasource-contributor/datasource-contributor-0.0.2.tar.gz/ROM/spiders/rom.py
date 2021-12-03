# -*- coding: utf-8 -*-
import scrapy
import requests
# from fake_useragent import UserAgent
from ROM.items import RomItem


# ua = UserAgent()

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
            name = i.xpath('.//h2/a/text()').extract_first()
            content = i.xpath('./div/div[2]/div[1]/div/div[1]/div[1]/text()').extract_first()
            url = i.xpath('.//h2/a/@href').extract_first()
            ye = url.split('/')[-1]
            json_url = 'https://controllerdatia.lacity.org/api/views/' + ye + '.json'
            api_res = self.parse_url(json_url)
            down = api_res[0]
            tag = api_res[1]
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
            item['name'] = name
            item['content'] = content
            item['url'] = url
            item['downloads'] = down
            item['tag'] = tag
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
            print(sss)
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}
        res = requests.get(url, headers=headers)
        res_list = res.json()
        downloads = res_list["downloadCount"]
        try:
            if True:
                tag = res_list["tags"]
        except:
            tag = None
        return downloads, tag
