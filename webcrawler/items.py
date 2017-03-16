# -*- coding: utf-8 -*-

import scrapy


class Item(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    temp_filename = scrapy.Field()
    links = scrapy.Field()


class Parsed(scrapy.Item):
    url = scrapy.Field()
    links = scrapy.Field()
    text = scrapy.Field()
    meta = scrapy.Field()