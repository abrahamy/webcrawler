# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Raw(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    filename = scrapy.Field()


class Metadata(scrapy.Item):
    title = scrapy.Field()
    identifier = scrapy.Field()
    source = scrapy.Field()
    type = scrapy.Field()
    content_type_hint = scrapy.Field()
    format = scrapy.Field()
    description = scrapy.Field()
    language = scrapy.Field()
    created = scrapy.Field()
    creator = scrapy.Field()
    contributor = scrapy.Field()
    modified = scrapy.Field()
    modifier = scrapy.Field()
    original_resource_name = scrapy.Field()
    print_date = scrapy.Field()
    publisher = scrapy.Field()
    rating = scrapy.Field()
    keywords = scrapy.Field()
    comments = scrapy.Field()
    rights = scrapy.Field()
    relation = scrapy.Field()
    meta_data_date = scrapy.Field()
    content = scrapy.Field()