# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018

import os
import datetime
import scrapy
import tika  # initializes tika.ServerEndPoint from environment variables
from tika import parser
import webcrawler.items as items
from webcrawler.models import Document


class ItemPipeline(object):

    def process_item(self, item: items.Item, spider: scrapy.spiders.CrawlSpider):
        '''
        Takes an instance of webcrawler.items.Item and parses the content using Tika RestAPI

        :param item: the item downloaded by the webcrawler
        :param spider: the spider with which the page was crawled
        '''
        try:
            parse_result = parser.from_file(item['path'])
            self.store(parse_result, item, spider)

        except:
            spider.logger.exception(
                'Failed to parse content of "{}"'.format(item['url'])
            )
        finally:
            item['path'].unlink()

        raise scrapy.exceptions.DropItem('Finished processing the item.')

    def store(self, parse_result, item: items.Item, spider: scrapy.spiders.CrawlSpider):
        '''
        Stores contents of crawled web pages/documents in the database with
        their associated Full Text Search index

        :param item: the item downloaded by the webcrawler
        :param spider: the spider with which the page was crawled
        :param parse_result: the result received from parsing the item using Apache Tika
        '''
        try:
            data = Document.get_fields_from_tika_metadata(
                parse_result['metadata']
            )
            data['text'] = parse_result.get('content', ''),
            data['url'] = item['url']
            data['crawl_date'] = datetime.datetime.now()
            data['links'] = item['external_urls']

            Document.create(**data)

        except:
            spider.logger.exception(
                'Failed to store metadata for {}'.format(item['url'])
            )
