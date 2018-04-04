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
import mimetypes
import scrapy
import logging
import webcrawler.items as items
from tika import tika, parser
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
from webcrawler.models import Document

tika.ServerHost = get_project_settings().get('TIKA_SERVER_HOST')
tika.TikaClientOnly = True

logger = logging.getLogger(__name__)


class ImageParser(ImagesPipeline):
    '''
    Stores images along with their context (i.e. the text of the page where the images where extracted)
    '''

    def item_completed(self, results, item, info):
        for (downloaded, file_info) in results:
            if not downloaded:
                continue

            data = {
                'url': file_info['url'],
                'text': item['text'],
                'crawl_date': datetime.datetime.now()
            }

            content_type = mimetypes.guess_type(file_info['path'])[0]
            if content_type is not None:
                data['content_type'] = content_type

            try:
                Document.create(**data)
            except:
                logger.exception(
                    'Failed to index url and metadata for {}'.format(
                        file_info['url']
                    )
                )

            # delete the file so that we don't fill up the disk space
            os.remove(file_info['path'])

        raise DropItem


class FileParser(FilesPipeline):
    '''
    Parse files with Tika and index them
    '''

    def index_items(self, parsed_items):
        for item in parsed_items:
            data = Document.get_fields_from_tika_metadata(item['meta'])
            data['text'] = item['text']
            data['url'] = item['url']
            data['crawl_date'] = datetime.datetime.now()

            try:
                Document.create(**data)
            except:
                logger.exception(
                    'Failed to index url and metadata for {}'.format(
                        item['url']
                    )
                )

    def item_completed(self, results, item, info):
        parsed_items = []
        for (downloaded, file_info) in results:
            if not downloaded:
                continue

            try:
                parsed = parser.from_file(file_info['path'])
                parsed_items.append(
                    items.Parsed(
                        url=file_info['url'],
                        text=parsed.get('content', ''),
                        meta=parsed['metadata']
                    )
                )
            except:
                logger.exception(
                    'Failed to index url and metadata for {}'.format(
                        file_info['url']
                    )
                )

            # delete the file so that we don't fill up the disk space
            os.remove(file_info['path'])

        self.index_items(parsed_items)

        raise DropItem


class MediaParser(object):
    '''
    Store audio/video information in the database
    '''

    def process_item(self, item, spider):
        '''Process Media items'''
        if not isinstance(item, items.Media):
            return item

        for link in item['media_links']:
            data = {
                'url': link.url,
                'text': link.text,
                'crawl_date': datetime.datetime.now()
            }

            content_type = mimetypes.guess_type(link.url)[0]
            if content_type is not None:
                data['content_type'] = content_type

            try:
                Document.create(**data)
            except:
                logger.exception(
                    'Failed to index url and metadata for {}'.format(
                        link.url
                    )
                )

        raise DropItem


class WebPageParser(object):

    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Item and parses the content using Tika RestAPI
        Returns an instance of webcrawler.items.Parsed
        '''
        if not isinstance(item, items.WebPage):
            return item

        try:
            parsed = parser.from_file(item['temp_filename'])

            return items.Parsed(
                url=item['url'],
                external_urls=item['external_urls'],
                text=parsed.get('content', ''),
                meta=parsed['metadata']
            )

        except:
            logger.exception(
                'Failed to parse content of "{}"'.format(item['url'])
            )

        # delete the temporary file
        os.remove(item['temp_filename'])

        raise DropItem


class Indexer(object):
    '''
    Stores the contents of crawled web pages/documents in the database with
    their associated Full Text Search index
    '''

    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Parsed generates a full text search Index
        for the content and persists the index and metadata
        '''
        if not isinstance(item, items.Parsed):
            return item

        data = Document.get_fields_from_tika_metadata(item['meta'])
        data['text'] = item['text']
        data['url'] = item['url']
        data['crawl_date'] = datetime.datetime.now()
        data['links'] = item['external_urls']

        try:
            Document.create(**data)
        except:
            logger.exception(
                'Failed to index url and metadata for {}'.format(item['url'])
            )

        raise DropItem
