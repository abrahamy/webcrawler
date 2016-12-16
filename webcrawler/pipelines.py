# -*- coding: utf-8 -*-

import os
from tika import tika, parser
from scrapy.exceptions import DropItem
from webcrawler.items import Document, Item, Parsed


tika.TikaClientOnly = True


class ContentParser(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Item and parses the content using Tika RestAPI
        Returns an instance of webcrawler.items.Parsed
        '''
        try:
            if type(item) is not Item:
                spider.logger.warning(
                    'ContentParser expects item to be an instance of webcrawler.items.Item \
                    got {} instead.'.format(
                        '.'.join([item.__class__.__module__, item.__class__.__name__])
                    )
                )
                
                return item

            parsed = parser.from_file(item['temp_filename'])

            return Parsed(
                url=item['url'],
                links=item['links'],
                text=parsed.get('content', ''),
                meta=parsed['metadata']
            )

        except:
            spider.logger.warning(
                'Failed to parse content of "{}"'.format(item['url'])
            )
        finally:
            if isinstance(item, Item):
                # delete the temporary file
                os.remove(item['temp_filename'])
        
        raise DropItem


class FTSIndexer(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Parsed generates a full text search Index
        for the content and persists the index and metadata
        '''
        try:
            if type(item) is not Parsed:
                spider.logger.warning(
                    'FTSIndexer expects item to be an instance of \
                    webcrawler.items.Parsed got {} instead'.format(
                        '.'.join([item.__class__.__module__, item.__class__.__name__])
                    )
                )

                raise DropItem
            
            doc_fields = Document.get_fields_from_tika_metadata(item['meta'])
            doc_fields['text'] = item['text']
            doc_fields['url'] = item['url']
            doc_fields['links_to'] = item['links']

            Document.create(**doc_fields)

            return None

        except:
            spider.logger.warning(
                'Failed to index url and metadata for {}'.format(item['url']),
                exec_info=True
            )