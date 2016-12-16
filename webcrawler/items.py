# -*- coding: utf-8 -*-

import datetime, json, scrapy
from peewee import (
    CharField, DateTimeField, TextField, ForeignKeyField,
    Model, SelectQuery, fn, IntegrityError
)
from playhouse.db_url import connect
from playhouse.postgres_ext import ArrayField, TSVectorField, Match
from playhouse.signals import post_save
from playhouse.shortcuts import model_to_dict
from scrapy.utils.project import get_project_settings


DOC_FIELD_TO_TIKA_META = {
    'content_type': ['Content-Type', 'Content-Type-Hint'],
    'contributor': 'dc:contributor',
    'coverage': 'dc:coverage',
    'created': 'dcterms:created',
    'creator': 'dc:creator',
    'date': 'dc:date',
    'description': 'dc:description',
    'format': 'dc:format',
    'identifier': 'dc:identifier',
    'language': 'dc:language',
    'modified': 'dcterms:modified',
    'publisher': 'dc:publisher',
    'relation': 'dc:relation',
    'rights': 'dc:rights',
    'source': 'dc:source',
    'subject': 'dc:subject',
    'title': 'dc:title',
    'type': 'dc:type',
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
    db_uri = get_project_settings().get('DATABASE_URI')
    return connect(db_uri)


class BaseModel(Model):

    def save(self, **kwargs):
        if not self.table_exists():
            self.create_table()
        
        return super().save(**kwargs)

    class Meta:
        database = get_db()


class Document(BaseModel):
    url = CharField(unique=True)
    content_type = CharField()
    contributor = CharField()
    coverage = CharField()
    created = DateTimeField()
    creator = CharField()
    date = DateTimeField()
    description = TextField()
    format = CharField()
    identifier = CharField()
    language = CharField()
    modified = DateTimeField()
    publisher = CharField()
    relation = CharField()
    rights = CharField()
    source = CharField()
    subject = TextField()
    title = TextField()
    type = CharField()
    text = TextField()
    links_to = ArrayField(CharField) # May be used by page ranking algorithm in the future

    @classmethod
    def create(cls, **query):
        '''
        Override create method to perform an update on duplicate Document.url
        '''
        try:
            instance = super().create(**query)
        except IntegrityError as e:
            instance = Document.select(Document.url==query.pop('url')).get()
            instance.update(**query)
        
        return instance
    
    @staticmethod
    def get_fields_from_tika_metadata(metadata):
        fields = {}

        for key, value in DOC_FIELD_TO_TIKA_META:
            if type(value) is list:
                # get the data of the first key in value that matches a key in the metadata
                for k in value:
                    v = metadata.get(k)
                    fields[key] = v
                    if v:
                        break
            else:
                fields[key] = metadata.get(value)
        
        return fields

    @staticmethod
    def fulltext_search(term, page_number=1, items_per_page=20, return_json=True):
        '''
        Execute a full text search query on the model and return a paginated result
        of matching records in JSON format or as model instances
        '''
        query = (Document
                    .select()
                    .join(Search, on=Search.document)
                    .where(
                        Match(Search.text, term) |
                        Match(Search.subject, term) |
                        Match(Search.title, term) |
                        Match(Search.description, term) |
                        Match(Search.creator, term) |
                        Match(Search.contributor, term) |
                        Match(Search.publisher, term)
                    ).paginate(page_number, items_per_page))

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
        
        fields_to_exclude = ['links_to', 'meta']
        object_list = map(
            lambda model: model_to_dict(model, exclude=fields_to_exclude), query
        )
        
        return json.dumps(list(object_list))


class Search(BaseModel):
    document = ForeignKeyField(Document, unique=True)
    subject = TSVectorField()
    title = TSVectorField()
    description = TSVectorField()
    creator = TSVectorField()
    contributor = TSVectorField()
    publisher = TSVectorField()
    text = TSVectorField()


@post_save(sender=Document)
def create_search_index(model_class, instance, created):
    '''
    Creates a fulltext searchable model derived from the document model
    each time a Document model is created
    '''
    fields = {
        'document': instance,
        'subject': fn.to_tsvector(instance.subject),
        'title': fn.to_tsvector(instance.title),
        'description': fn.to_tsvector(instance.description),
        'creator': fn.to_tsvector(instance.creator),
        'contributor': fn.to_tsvector(instance.contributor),
        'publisher': fn.to_tsvector(instance.publisher),
        'text': fn.to_tsvector(instance.text)
    }

    # if the Document already have a Search model update that instead
    try:
        return Search.create(**fields)
    except IntegrityError as e:
        search = Search.select(Search.document==instance).get()
        search.update(**fields)
        return search