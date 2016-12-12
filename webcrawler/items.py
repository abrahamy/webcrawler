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
    
    def fulltext_search(self, term, page_number=1, items_per_page=20, return_json=True):
        '''
        Execute a full text search query on the model and return a paginated result
        of matching records in JSON format or as model instances
        '''
        results = Archive.select().where(
            Match(Archive.search, term) |
            Match(Archive.metadata['title'], term) |
            Match(Archive.metadata['description'], term)
        ).paginate(page_number, items_per_page)

        if return_json:
            res
        
        return results
    
    def to_json(self, query=None):
        '''
        Return the list of models in the query as a JSON array if a SelectQuery
        is given otherwise return the current model instance as a JSON object
        @TODO: clean the metadata field
        '''
        to_dict = lambda m: model_to_dict(m, only=['url', 'metadata'])

        if not query:
            return json.dumps(to_dict(self))
        
        if type(query) is not SelectQuery:
            raise ValueError
        
        results = []
        for model in query:
            results.append(to_dict(model))
        
        return json.dumps(results)
    
    class Meta:
        database = get_db()