# -*- coding: utf-8 -*-

import json, scrapy
from dateutil.parser import parse
from peewee import (
    CharField, CompositeKey, create_model_tables, DateTimeField,
    TextField, FloatField, Model, SelectQuery, SQL, IntegrityError,
    ForeignKeyField,
)
from playhouse.fields import ManyToManyField
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict
from scrapy.utils.project import get_project_settings


DOC_FIELD_TO_TIKA_META = {
    'content_type': ['Content-Type', 'Content-Type-Hint'],
    'created': 'dcterms:created',
    'creator': 'dc:creator',
    'date': 'dc:date',
    'description': 'dc:description',
    'language': 'dc:language',
    'modified': 'dcterms:modified',
    'publisher': 'dc:publisher',
    'source': 'dc:source',
    'subject': 'dc:subject',
    'title': 'dc:title',
    'text': 'content'
}


class Item(scrapy.Item):
    '''
    Returns the crawled url and a file-like object representing the content
    '''
    url = scrapy.Field()
    temp_filename = scrapy.Field()
    links = scrapy.Field()


class Parsed(scrapy.Item):
    url = scrapy.Field()
    links = scrapy.Field()
    text = scrapy.Field()
    meta = scrapy.Field()


def get_db():
    '''Create a new database connection'''
    db_settings = get_project_settings().getdict('CMSL_BOT_DATABASE')
    return PooledMySQLDatabase(
        db_settings.pop('name'),
        **db_settings
    )


class BaseModel(Model):

    class Meta:
        database = get_db()


class Document(BaseModel):
    url = CharField(unique=True)
    content_type = CharField(null=True)
    created = DateTimeField(null=True)
    creator = CharField(null=True)
    date = DateTimeField(null=True)
    description = TextField(null=True)
    language = CharField(null=True)
    modified = DateTimeField(null=True)
    publisher = CharField(null=True)
    source = CharField(null=True)
    subject = TextField(null=True)
    title = TextField(null=True)
    text = TextField(null=True)
    # The page rank will be computed and be stored in the following field
    page_rank = FloatField(default=0.0)

    @classmethod
    def create(cls, **query):
        '''
        Override create method to perform an update on duplicate Document.url
        '''
        instance = cls.get_or_create(url=query.pop('url'))[0]
        instance.update(**query)

        return instance
    
    def add_links(self, urls):
        '''
        Store links extracted from this document.

        Args:
            urls (set<str>): A set of urls that this document points to
        '''
        self.links.clear()
        for url in urls:
            self.links.add(Link.create(document=self, url=url), False)

    @staticmethod
    def get_fields_from_tika_metadata(metadata):
        fields = {}

        for key, value in DOC_FIELD_TO_TIKA_META.items():
            if type(value) is list:
                # get the data of the first key in value that matches a key in the metadata
                for k in value:
                    v = metadata.get(k)
                    fields[key] = v
                    if v:
                        break
            else:
                fields[key] = metadata.get(value)

        # parse the datetime strings from tika metadata into
        # python datetime objects
        date_fields = ['created', 'date', 'modified']
        for field in date_fields:
            value = fields[field]
            if value and isinstance(value, str):
                fields[field] = parse(value)

        return fields

    @staticmethod
    def fulltext_search(term, page_number=1, items_per_page=20, return_json=True):
        '''
        Execute a full text search query on the model and return a paginated result
        of matching records in JSON format or as model instances
        '''
        query = (Document
                    .select()
                    .where(SQL(
                        '''
                        MATCH (
                            `text`, subject, title, description, creator, publisher
                        ) AGAINST (%s IN NATURAL LANGUAGE MODE)
                        ''', term
                    )).paginate(page_number, items_per_page))

        if return_json:
            return Document.to_json(query)

        return query

    @staticmethod
    def to_json(query):
        '''
        Return the list of models in the query as a JSON array given a SelectQuery
        '''
        if type(query) is not SelectQuery:
            raise ValueError

        object_list = []
        for model in query:
            model_dict = {
                'url': model.url,
                'content_type': model.content_type,
                'language': model.language,
                'title': model.title,
                'subject': model.subject,
                'description': model.description,
                'creator': model.creator,
                'created': model.created,
                'modified': model.modified
            }

            object_list.append(model_dict)

        return json.dumps(object_list)
    
    class Meta:
        constraints = [
            SQL("FULLTEXT(`text`, subject, title, description, creator, publisher)")
        ]


class Link(BaseModel):
    document = ForeignKeyField(Document, related_name='links')
    url = CharField()
    
    class Meta:
        primary_key = CompositeKey('document', 'url')


def initialize_database():
    create_model_tables([Document, Link], fail_silently=True)