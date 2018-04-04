# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import collections
import tempfile
import scrapy
import webcrawler.items as items
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from webcrawler.mixins import LinkExtractionMixin
from webcrawler.models import URLConfig


class WebSpider(CrawlSpider, LinkExtractionMixin):
    '''Crawl and index the Internet! (If it can)'''
    name = 'web'
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    custom_settings = {
        'LOG_FILE': '/var/log/webcrawler/web.log',
        # Avoid redownloading pages that have been downloaded in the last twelve hours
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 12 * 60 * 60
    }
    # restart spider every time urls change
    __hashed_urls = None

    @property
    def start_urls(self):
        '''Get start urls from the database'''
        _start_urls = URLConfig.get(URLConfig.spider == 'web').start_urls

        if self.__hashed_urls is None:
            self.__hashed_urls = hash(tuple(_start_urls))

        return list(_start_urls)

    def start_urls_changed(self):
        '''
        Check if the `start_urls` have changed

        Returns:
            boolean: return True if the `start_urls` have changed and false otherwise
        '''
        start_urls_set = set(self.start_urls)
        new_hashed_urls = hash(tuple(start_urls_set))

        return new_hashed_urls == self.__hashed_urls

    def parse_item(self, response: scrapy.http.Response):
        '''
        Parse a response into an instance of webcrawler.items.Item
        Skips a response if it is not a HtmlResponse
        '''
        if self.start_urls_changed():
            # the spider will be automatically restarted by supervisord
            raise CloseSpider

        crawled_items = []
        if not isinstance(response, scrapy.http.HtmlResponse):
            # do nothing (i.e. skip handling)
            return crawled_items

        # media links will not be processed but simply indexed in the database
        media_links = self.extract_audio_links(response)
        media_links.extend(self.extract_video_links(response))
        crawled_items.append(items.Media(media_links=media_links))

        # documents that can be parsed for their content with Tika server
        file_urls = self.map_links_to_urls(
            self.extract_document_links(response))
        crawled_items.append(
            items.Files(file_urls=file_urls)
        )

        # images will not be parsed but simply indexed in the database
        image_urls = self.map_links_to_urls(self.extract_image_links(response))
        # Use the text on the page where these images have been extracted as a context
        # when searching for images
        search_context = ''.join(
            response.selector.xpath('//body//text()').extract()
        ).strip()
        crawled_items.append(
            items.Images(
                image_urls=image_urls,
                text=search_context
            )
        )

        # external urls will be associated with their source url,
        # this may be used later for implementing page_rank algorithm
        external_urls = self.extract_document_links(response)

        try:
            with tempfile.NamedTemporaryFile(delete=False) as stream:
                stream.write(response.body)
                crawled_items.append(
                    items.WebPage(
                        url=response.url,
                        external_urls=external_urls,
                        temp_filename=stream.name
                    )
                )

        except OSError:
            self.logger.error(
                'Failed to save response.body to temporary file', exec_info=True
            )

        return crawled_items

    @staticmethod
    def map_links_to_urls(links):
        '''Takes an iterable of links and returns a list of url strings'''
        assert(isinstance(links, collections.Iterable))
        return [link.url for link in links]
