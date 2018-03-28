# -*- coding: utf-8 -*-
from webcrawler.models import NewsConfig
from .web import WebSpider


class NewsSpider(WebSpider):
    name = 'newspider'
    custom_settings = {}

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        news_urls = NewsConfig.get().news_urls
        return list(news_urls)
