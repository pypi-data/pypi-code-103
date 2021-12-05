# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CitybrainSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Name = scrapy.Field()
    Description = scrapy.Field()
    Link_url = scrapy.Field()
    Tags = scrapy.Field()
    Rows = scrapy.Field()
    Dataset_Owner = scrapy.Field()
    Source_Link = scrapy.Field()
    Category = scrapy.Field()
