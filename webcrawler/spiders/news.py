# -*- coding: utf-8 -*-
import time
import scrapy
from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider
from webcrawler.models import URLConfig
from .web import WebSpider


class NewsSpider(WebSpider):
    name = 'news'
    custom_settings = {
        'LOG_FILE': '/var/log/webcrawler/news.log',
        # disable caching, always redownload pages.
        'HTTPCACHE_ENABLED': False,
        'HTTPCACHE_EXPIRATION_SECS': 0
    }
    spider_start_time = time.time()
    restart_interval = 2 * 60 * 60  # restart after two hours (in seconds)

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        _start_urls = URLConfig.get(URLConfig.spider == 'news').start_urls
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
