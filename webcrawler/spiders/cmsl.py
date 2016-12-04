# -*- coding: utf-8 -*-
import tempfile
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from webcrawler.items import Raw


def is_new_or_stale(link):
    '''
    If link has been crawled check staleness using etag & last-modified headers.
    If fresh return None to discard link.
    '''
    return link # @TODO: Implement this


class CmslSpider(CrawlSpider):
    name = 'cmsl'
    start_urls = [
            'http://www.nairaland.com/',
            'http://www.lindaikejisblog.com/',
            'https://www.reddit.com/',
            'https://news.ycombinator.com/',
        ]

    rules = (
        Rule(LinkExtractor(process_value=is_new_or_stale), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as stream:
                stream.write(response.body)
                filename = stream.name

        except OSError as e:
            filename = None
        
        item = Raw(url=response.url, filename=filename)
        return item
