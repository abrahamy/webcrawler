# -*- coding: utf-8 -*-

import scrapy


class Item(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    temp_filename = scrapy.Field()
    files = scrapy.Field()              # required by scrapy.pipelines.FilesPipeline
    images = scrapy.Field()             # required by scrapy.pipelines.ImagesPipeline
    file_urls = scrapy.Field()          # required by scrapy.pipelines.FilesPipeline
    image_urls = scrapy.Field()         # required by scrapy.pipelines.ImagesPipeline
    external_urls = scrapy.Field()      # renamed from `links` to `external_urls`
    media_links = scrapy.Field()


class Parsed(scrapy.Item):
    url = scrapy.Field()
    links = scrapy.Field()
    text = scrapy.Field()
    meta = scrapy.Field()
