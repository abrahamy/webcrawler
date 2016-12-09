# -*- coding: utf-8 -*-

import datetime, scrapy
from peewee import CharField, DateTimeField, Model
from playhouse.db_url import connect
from playhouse.postgres_ext import BinaryJSONField, TSVectorField
from scrapy.utils.project import get_project_settings


class Raw(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    filename = scrapy.Field()


class CrawlData(scrapy.Item):
    url = scrapy.Field()
    content = scrapy.Field()
    meta = scrapy.Field()


def get_db():
    db_uri = get_project_settings().get('DATABASE_URI')
    return connect(db_uri)


class Archive(Model):
    url = CharField(255, unique=True)
    search = TSVectorField()
    metadata = BinaryJSONField()
    created_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(null=True)

    def __repr__(self):
        return '<Archive(id="{}", url="{}")>'.format(self.id, self.url)
    
    def save(self, **kwargs):
        '''
        Create the table for this model if it does not exist before attempting to save
        '''
        db = self._meta.database
        with db.atomic():
            self.create_table(True)

        return super().save(**kwargs)
    
    class Meta:
        database = get_db()