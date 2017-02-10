# -*- coding: utf-8 -*-

import json, scrapy
from dateutil.parser import parse
from peewee import (
    CharField, DateTimeField, TextField, ForeignKeyField,
    Model, SelectQuery, fn, IntegrityError
)
from playhouse.db_url import connect
from playhouse.postgres_ext import ArrayField, TSVectorField
from playhouse.pool import PooledPostgresqlExtDatabase
from playhouse.shortcuts import model_to_dict
from scrapy.utils.project import get_project_settings
from .stopwords import strip_stopwords


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


class SparseTextField(TextField):
    '''
    Use NLTK to preprocess text in order to eliminate stop words
    and reduce data storage space
    '''

    def coerce(self, value):
        '''
        Strip text of stop words and redundant whitespace
        '''
        sparse_text = strip_stopwords(value)
        return super().coerce(sparse_text)


def get_db():
    '''Create a new database connection'''
    db_settings = get_project_settings().getdict('CMSL_BOT_DATABASE')
    return PooledPostgresqlExtDatabase(
        db_settings.pop('name'),
        **db_settings
    )


class BaseModel(Model):

    class Meta:
        database = get_db()


class Document(BaseModel):
    url = CharField(unique=True)
    content_type = CharField(null=True)
    contributor = CharField(null=True)
    coverage = CharField(null=True)
    created = DateTimeField(null=True)
    creator = CharField(null=True)
    date = DateTimeField(null=True)
    description = TextField(null=True)
    format = CharField(null=True)
    identifier = CharField(null=True)
    language = CharField(null=True)
    modified = DateTimeField(null=True)
    publisher = CharField(null=True)
    relation = CharField(null=True)
    rights = CharField(null=True)
    source = CharField(null=True)
    subject = TextField(null=True)
    title = TextField(null=True)
    type = CharField(null=True)
    text = SparseTextField(null=True)
    # The next field may be required for page ranking algorithm in the future
    links_to = ArrayField(CharField, default=[])

    @classmethod
    def create(cls, **query):
        '''
        Override create method to perform an update on duplicate Document.url
        '''
        try:
            instance = super().create(**query)
        except IntegrityError as e:
            cls._meta.database.rollback()
            instance = Document.select(Document.url==query.pop('url')).get()
            instance.update(**query)

        instance.create_search_model()

        return instance

    def create_search_model(self):
        '''
        Creates a full text searchable model derived from this instance
        '''
        fields = {
            'document': self,
            'subject': fn.to_tsvector(self.subject),
            'title': fn.to_tsvector(self.title),
            'description': fn.to_tsvector(self.description),
            'creator': fn.to_tsvector(self.creator),
            'contributor': fn.to_tsvector(self.contributor),
            'publisher': fn.to_tsvector(self.publisher),
            'text': fn.to_tsvector(self.text)
        }
        # if the Document already have a Search model update that instead
        try:
            return Search.create(**fields)
        except IntegrityError as e:
            self._meta.database.rollback()
            search = Search.select(Search.document==self).get()
            search.update(**fields)
            return search

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
                    .join(Search, on=Search.document)
                    .where(
                        Search.text.match(term) |
                        Search.subject.match(term) |
                        Search.title.match(term) |
                        Search.description.match(term) |
                        Search.creator.match(term) |
                        Search.contributor.match(term) |
                        Search.publisher.match(term)
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

        object_list = []
        for model in query:
            model_dict = {
                'url': model.url,
                'content_type': model.content_type,
                'format': model.format,
                'language': model.language,
                'title': model.title,
                'subject': model.subject,
                'description': model.description,
                'creator': model.creator,
                'created': model.created,
                'modified': model.modified
            }

            object_list.append(model_dict)

        return json.dumps(list(object_list), indent=2)


class Search(BaseModel):
    document = ForeignKeyField(Document, unique=True)
    subject = TSVectorField(null=True)
    title = TSVectorField(null=True)
    description = TSVectorField(null=True)
    creator = TSVectorField(null=True)
    contributor = TSVectorField(null=True)
    publisher = TSVectorField(null=True)
    text = TSVectorField(null=True)


def create_schema(models):
    '''Create tables for the given models if non existent'''
    if not isinstance(models, (list, tuple)):
        raise TypeError

    if len(models):
        database = models[0]._meta.database

        with database.atomic():
            database.create_tables(models, safe=True)