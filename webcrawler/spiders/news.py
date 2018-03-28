# -*- coding: utf-8 -*-
from .web import WebSpider


class NewsSpider(WebSpider):
    name = 'newspider'

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        raise Exception('Not Implemented')
