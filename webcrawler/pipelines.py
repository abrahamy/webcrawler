# -*- coding: utf-8 -*-

import datetime, os, tika
from tika import parser
from peewee import fn, IntegrityError
from scrapy.exceptions import DropItem
from webcrawler.items import Archive, CrawlData, Raw


tika.TikaClientOnly = True


class ContentParser(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Raw and parses the content using Tika RestAPI
        Returns an instance of webcrawler.items.CrawlData
        '''
        try:
            if type(item) is not Raw:
                spider.logger.warning(
                    'ContentParser expects item to be an instance of webcrawler.items.Raw \
                    but got {} instead.'.format(
                        '.'.join([item.__class__.__module__, item.__class__.__name__])
                    )
                )
                
                return item

            parsed = parser.from_file(item['filename'])

        except:
            spider.logger.warning('Failed to parse content of "{}"'.format(item['url']))
            raise DropItem
        finally:
            # delete the temporary file
            os.remove(item['filename'])

        # create an instance of webcrawler.items.CrawlData
        data = CrawlData(
            url=item['url'],
            content=parsed.get('content', ''),
            meta=parsed.get('metadata', {})
        )

        return data


class FTSIndexer(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.CrawlData generates a full text search Index
        for the content and persists the index and metadata
        '''
        try:
            if type(item) is not CrawlData:
                spider.logger.warning(
                    'FTSIndexer expects item to be an instance of \
                    webcrawler.items.CrawlData but got {} instead'.format(
                        '.'.join([item.__class__.__module__, item.__class__.__name__])
                    )
                )

                raise DropItem

            Archive.create(
                url=item['url'],
                search=fn.to_tsvector(item['content']),
                metadata=item['meta']
            )

            return None

        except IntegrityError as e:
            '''
            This URL has been been indexed before. Just regenerate index in case the
            content has changed.
            '''
            Archive.update(
                search=fn.to_tsvector(item['content']),
                metadata=item['meta'],
                modified_date=datetime.datetime.now()
            )