# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import tempfile
import scrapy
from pathlib import Path
from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from webcrawler.items import Item
from webcrawler.models import URLConfig


link_extractor = LinkExtractor(
    tags=("a", "area", "audio", "embed", "img", "source", "track", "video"),
    attrs=("href", "src"),
    deny_extensions=(),
)


class WebSpider(CrawlSpider):
    """Crawl and index the Internet! (If it can)"""
    name = "web"
    rules = (Rule(link_extractor, callback="parse_item", follow=True),)
    custom_settings = {
        # Avoid redownloading pages that have been downloaded in the last twelve hours
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_EXPIRATION_SECS": 12 * 60 * 60,
    }
    # restart spider every time urls change
    __hashed_urls = None

    @property
    def start_urls(self):
        """Get start urls from the database"""
        _start_urls = URLConfig.get(URLConfig.spider == "web").start_urls

        if self.__hashed_urls is None:
            self.__hashed_urls = hash(tuple(_start_urls))

        return list(_start_urls)

    def start_urls_changed(self):
        """
        Check if the `start_urls` have changed

        Returns:
            boolean: return True if the `start_urls` have changed and false otherwise
        """
        start_urls_set = set(self.start_urls)
        new_hashed_urls = hash(tuple(start_urls_set))

        return new_hashed_urls == self.__hashed_urls

    def parse_item(self, response: scrapy.http.Response):
        """
        Parse a response into an instance of webcrawler.items.Item
        """
        if self.start_urls_changed():
            # the spider will be automatically restarted by supervisord
            raise CloseSpider(
                "`start_urls` have changed, restarting {} spider".format(self.name)
            )

        item_data = {
            "url": response.url,
            "external_urls": self.extract_external_urls(response),
        }

        suffix = Path(response.url).suffix or ""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as stream:
            stream.write(response.body)
            item_data["path"] = Path(stream.name)

        return [Item(**item_data)]

    @staticmethod
    def extract_external_urls(response: scrapy.http.Response):
        """Extract all external urls from this page"""
        if not isinstance(response, scrapy.http.HtmlResponse):
            return set([])

        parsed_url = urlparse(response.url)
        domain = (parsed_url.netloc,)

        _link_extractor = LinkExtractor(deny_domains=domain)
        urls = map(lambda link: link.url, _link_extractor.extract_links(response))

        return set(urls)
