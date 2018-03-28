# -*- coding: utf-8 -*-
import collections
import tempfile
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from webcrawler.mixins import LinkExtractionMixin
from webcrawler.items import Item


class WebSpider(CrawlSpider, LinkExtractionMixin):
    '''Crawl and index the Internet! (If it can)'''
    name = 'webspider'
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    custom_settings = {}

    @property
    def start_urls(self):
        '''Get start urls from settings'''
        self.settings.getlist('DEFAULT_START_URLS')

    def parse_item(self, response: scrapy.http.Response):
        '''
        Parse a response into an instance of webcrawler.items.Item
        Skips a response if it is not a HtmlResponse
        '''
        if not isinstance(response, scrapy.http.HtmlResponse):
            return []

        # media links will not be processed but simply indexed in the database
        media_links = self.extract_audio_links(response)
        media_links.extend(self.extract_video_links(response))

        # documents that can be parsed for their content with Tika server
        file_urls = self.map_links_to_urls(
            self.extract_document_links(response))

        # images will not be parsed but simply indexed in the database
        image_urls = self.map_links_to_urls(self.extract_image_links(response))

        # external urls will be associated with their source url,
        # this may be used later for implementing page_rank algorithm
        external_urls = self.extract_document_links(response)

        fields = {
            'url': response.url,
            'file_urls': file_urls,
            'image_urls': image_urls,
            'external_urls': external_urls,
            'media_links': media_links
        }

        try:
            with tempfile.NamedTemporaryFile(delete=False) as stream:
                stream.write(response.body)
                fields['temp_filename'] = stream.name

            return [Item(**fields)]

        except OSError:
            self.logger.error(
                'Failed to save response.body to temporary file', exec_info=True
            )

        return []

    @staticmethod
    def map_links_to_urls(links):
        '''Takes an iterable of links and returns a list of url strings'''
        assert(isinstance(links, collections.Iterable))
        return [link.url for link in links]
