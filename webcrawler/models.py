# Data Access Layer
import json
import peewee
from peewee import SQL
from playhouse.pool import PooledMySQLDatabase
from dateutil.parser import parse as parse_date
from .settings import CMSL_BOT_DATABASE as db_settings


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


def get_db():
    '''Create a new database connection'''
    global db_settings
    return PooledMySQLDatabase(
        db_settings.pop('name'),
        **db_settings
    )


class SetField(peewee.TextField):
    '''
    SetField stores a set of strings as a semicolon delimited string inside
    a text field in the database
    '''

    def db_value(self, value):
        if value is None:
            return

        if not isinstance(value, (list, tuple, set)):
            raise ValueError('Value must be a list, tuple or set of strings')

        value = map(lambda i: str(i), set(value))
        value_str = ';'.join(value)

        return super().db_value(value_str)

    def python_value(self, value):
        value = super().python_value(value)

        return set(value.split(';'))


class NewsConfig(peewee.Model):
    '''
    NewsConfig model is used by the `webcrawler.spiders.news.NewsSpider` to dynamically
    configure the crawler
    '''
    # Re-index news URLs after `restart_interval` hours
    restart_interval = peewee.FloatField(default=2.0)
    news_urls = SetField()

    @classmethod
    def create_or_update_news_config(cls, news_urls, restart_interval=2.0, append_urls=False):
        '''
        Ensures that only one instance of the news config exists

        Use only this method for saving news configs
        '''
        instance = None
        try:
            instance = cls.select().get()
            instance.news_urls = (instance.news_urls +
                                  news_urls) if append_urls else news_urls
        except peewee.DoesNotExist as _:
            instance = cls()
            instance.news_urls = news_urls

        instance.restart_interval = restart_interval
        return instance.save()


class Document(peewee.Model):
    url = peewee.CharField(unique=True)
    crawl_date = peewee.DateTimeField()
    content_type = peewee.CharField(null=True)
    created = peewee.DateTimeField(null=True)
    creator = peewee.CharField(null=True)
    date = peewee.DateTimeField(null=True)
    description = peewee.TextField(null=True)
    language = peewee.CharField(null=True)
    modified = peewee.DateTimeField(null=True)
    publisher = peewee.CharField(null=True)
    source = peewee.CharField(null=True)
    subject = peewee.TextField(null=True)
    title = peewee.TextField(null=True)
    text = peewee.TextField(null=True)
    # These fields may be used for implementing a page rank algorithm
    links = SetField(default=set())
    page_rank = peewee.FloatField(default=0.0)

    @classmethod
    def create(cls, **query):
        '''
        Override create method to perform an update on duplicate Document.url
        '''
        try:
            instance = super().create(**query)
        except peewee.IntegrityError as _:
            cls._meta.database.rollback()
            instance = cls.select().where(cls.url == query.pop('url')).get()
            instance.update(**query)

        return instance

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
                fields[field] = parse_date(value)

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
        if type(query) is not peewee.SelectQuery:
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
        database = get_db()
        constraints = [
            SQL("FULLTEXT(`text`, subject, title, description, creator, publisher)")
        ]


def initialize_database():
    Document.create_table(fail_silently=True)


initialize_database()
