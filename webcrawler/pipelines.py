# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import tika
from tika import parser
from scrapy.exceptions import DropItem
from webcrawler.items import Metadata


tika.TikaClientOnly = True


class TikaParser(object):
    def process_item(self, item, spider):
        '''
        Takes an instance of webcrawler.items.Raw and parses using a Tika RestAPI
        Returns an instance of webcrawler.items.Metadata
        '''
        try:
            parsed = parser.from_file(item.filename)
        except:
            spider.logger.warning('Failed to parse content of "{}"'.format(item.url))
            raise DropItem
        finally:
            # delete the temporary file
            os.remove(item.filename)

        # create an instance of webcrawler.items.Metadata
        content = parsed.get('content', '')
        parsed_meta = parsed.get('metadata', {})

        meta = Metadata(
            title=parsed_meta.get('title'),
            identifier=parsed_meta.get('identifier'),
            source=parsed_meta.get('source'),
            type=parsed_meta.get('type'),
            content_type_hint=parsed_meta.get('content_type_hint'),
            format=parsed_meta.get('format'),
            description=parsed_meta.get('description'),
            language=parsed_meta.get('language'),
            created=parsed_meta.get('created'),
            creator=parsed_meta.get('creator'),
            contributor=parsed_meta.get('contributor'),
            modified=parsed_meta.get('modified'),
            modifier=parsed_meta.get('modifier'),
            original_resource_name=parsed_meta.get('original_resource_name'),
            print_date=parsed_meta.get('print_date'),
            publisher=parsed_meta.get('publisher'),
            rating=parsed_meta.get('rating'),
            keywords=parsed_meta.get('keywords'),
            comments=parsed_meta.get('comments'),
            rights=parsed_meta.get('rights'),
            relation=parsed_meta.get('relation'),
            meta_data_date=parsed_meta.get('meta_data_date'),
            content=parsed_meta.get('content')
        )

        return meta


class MetadataPersister(object):
    def process_item(self, item, spider):
        pass


class Indexer(object):
    def process_item(self, item, spider):
        pass
