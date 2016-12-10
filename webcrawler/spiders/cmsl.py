# -*- coding: utf-8 -*-
import tempfile
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from webcrawler.items import Raw


# configure LinkExtractor to extract EVERY link!!!
link_extractor = LinkExtractor(
    tags=('a', 'area', 'img', 'source', 'track', 'embed'),
    attrs=('href', 'src'), deny_extensions=()
)


class CmslSpider(CrawlSpider):
    name = 'cmsl'
    start_urls = [
            'http://www.nairaland.com/',
            'http://www.lindaikejisblog.com/',
            'https://www.reddit.com/',
            'https://news.ycombinator.com/',
            'http://botid.org/',
        ]

    rules = (
        Rule(link_extractor, callback='parse_item', follow=True),
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
