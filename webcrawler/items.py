# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
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
