# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import time
import scrapy
from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider
from webcrawler.models import URLConfig
from .web import WebSpider


class NewsSpider(WebSpider):
    name = 'news'
    custom_settings = {
        # Cache pages for only 15 minutes.
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 15 * 60
    }
    spider_start_time = time.time()
    restart_interval = 2 * 60 * 60  # restart after two hours (in seconds)
    # restart spider every time urls change
    __hashed_urls = None

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        _start_urls = URLConfig.get(URLConfig.spider == 'news').start_urls

        if self.__hashed_urls is None:
            self.__hashed_urls = hash(tuple(_start_urls))

        return list(_start_urls)

    @property
    def allowed_domains(self):
        '''Restrict spider to crawl only domains in `start_urls`'''
        __allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        return __allowed_domains

    def parse_item(self, response: scrapy.http.Response):
        '''
        Overriding base `parse_item` to stop spider after two hours.
        Supervisord will automatically restart the spider when stopped.
        '''
        runtime = time.time() - self.spider_start_time
        if self.restart_interval <= runtime:
            raise CloseSpider('Restarting news spider')

        return super().parse_item(response)
