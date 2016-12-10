# -*- coding: utf-8 -*-
import tempfile
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from webcrawler.items import Raw


# configure LinkExtractor to extract EVERY link!!!
link_extractor = LinkExtractor(
    tags=('a', 'area', 'img', 'source', 'track', 'embed'),
    attrs=('href', 'src'), deny_extensions=()
)

def get_start_urls():
    '''
    Get start_urls from settings and cache the result
    '''
    settings = get_project_settings()
    return settings.getlist('DEFAULT_START_URLS')


class CmslSpider(CrawlSpider):
    name = 'cmsl'
    start_urls = get_start_urls()
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
