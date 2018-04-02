# -*- coding: utf-8 -*-
from webcrawler.models import Job
from .web import WebSpider


class NewsSpider(WebSpider):
    name = 'news'
    custom_settings = {}

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        news_urls = Job.get().news_urls
        return list(news_urls)
