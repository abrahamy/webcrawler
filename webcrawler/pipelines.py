# -*- coding: utf-8 -*-

import os, tika
from tika import parser
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
            assert(type(item)==Raw)
            parsed = parser.from_file(item['filename'])

        except AssertionError as e:
            spider.logger.warning(
                'ContentParser expects item to be an instance of webcrawler.items.Raw \
                but got {} instead.'.format(
                    '.'.join([item.__class__.__module__, item.__class__.__name__])
                )
            )

            return item
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


class DataPersister(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.CrawlData and persists it in the database
        '''
        try:
            assert(type(item)==CrawlData)

            model = Archive(
                id=Archive.gen_pk(), url=item['url'],
                data=item['content'], meta=item['meta']
            )

            model.save()
            return model

        except AssertionError as e:
            spider.logger.warning(
                'DataPersiter expects item to be an instance of \
                webcrawler.items.CrawlData but got {} instead'.format(
                    '.'.join([item.__class__.__module__, item.__class__.__name__])
                )
            )

            return item


class FTSIndexer(object):
    def process_item(self, item, spider):
        pass
