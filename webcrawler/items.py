# -*- coding: utf-8 -*-

import scrapy


class WebPage(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    temp_filename = scrapy.Field()
    external_urls = scrapy.Field()


class Images(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()
    text = scrapy.Field()


class Files(scrapy.Item):
    files = scrapy.Field()
    file_urls = scrapy.Field()


class Media(scrapy.Item):
    media_links = scrapy.Field()


class Parsed(scrapy.Item):
    url = scrapy.Field()
    external_urls = scrapy.Field()
    text = scrapy.Field()
    meta = scrapy.Field()
