# -*- coding: utf-8 -*-
import tempfile
import scrapy
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from webcrawler.items import Item


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
        '''
        Parse a response into an instance of webcrawler.items.Item
        '''
        try:
            fields = {
                'url': response.url,
                'links': self.extract_external_links(response)
            }

            with tempfile.NamedTemporaryFile(delete=False) as stream:
                stream.write(response.body)
                fields['temp_filename'] = stream.name
            
            return Item(**fields)

        except OSError:
            self.logger.error(
                'Failed to save response.body to temporary file', exec_info=True
            )
    
    @staticmethod
    def extract_external_links(response):
        '''
        Extract all external links from this page
        '''
        if not isinstance(response, scrapy.http.HtmlResponse):
            return []
        
        parsed_url = urlparse(response.url)
        domain = (parsed_url.netloc,)

        link_extractor = LinkExtractor(deny_domains=domain)
        links = map(lambda link: link.url, link_extractor.extract_links(response))

        return list(links)