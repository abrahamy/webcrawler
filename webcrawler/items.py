# -*- coding: utf-8 -*-

import datetime, json, scrapy
from peewee import CharField, DateTimeField, Model, SelectQuery
from playhouse.db_url import connect
from playhouse.postgres_ext import BinaryJSONField, TSVectorField, Match
from playhouse.shortcuts import model_to_dict
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
    
    @classmethod
    def fulltext_search(cls, term, page_number=1, items_per_page=20, return_json=True):
        '''
        Execute a full text search query on the model and return a paginated result
        of matching records in JSON format or as model instances
        '''
        results = cls.select().where(
            Match(cls.search, term) |
            Match(cls.metadata['title'], term) |
            Match(cls.metadata['description'], term)
        ).paginate(page_number, items_per_page)

        if return_json:
            return cls.to_json(results)
        
        return results
    
    @staticmethod
    def to_json(query):
        '''
        Return the list of models in the query as a JSON array given a SelectQuery
        @TODO: clean the metadata field
        '''
        if type(query) is not SelectQuery:
            raise ValueError
        
        only_fields = ['url', 'metadata']
        results = []
        for model in query:
            results.append(model_to_dict(model, only=only_fields))
        
        return json.dumps(results)
    
    class Meta:
        database = get_db()