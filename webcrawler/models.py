# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import logging
import datetime
import peewee
from peewee import SQL
from playhouse.pool import PooledMySQLDatabase
from dateutil.parser import parse as parse_date
from .settings import CMSL_BOT_DATABASE as db_settings


DOC_FIELD_TO_TIKA_META = {
    "content_type": ["Content-Type", "Content-Type-Hint"],
    "created": "dcterms:created",
    "creator": "dc:creator",
    "date": "dc:date",
    "description": "dc:description",
    "language": "dc:language",
    "modified": "dcterms:modified",
    "publisher": "dc:publisher",
    "source": "dc:source",
    "subject": "dc:subject",
    "title": "dc:title",
    "text": "content",
}


def get_db():
    """Create a new database connection"""
    global db_settings
    return PooledMySQLDatabase(db_settings.pop("name"), **db_settings)


DB = get_db()


class SetField(peewee.TextField):
    """
    SetField stores a set of strings as a semicolon delimited string inside
    a text field in the database
    """

    def db_value(self, value):
        if value is None:
            return

        if not isinstance(value, (list, tuple, set)):
            raise ValueError("Value must be a list, tuple or set of strings")

        value = map(lambda i: str(i), set(value))
        value_str = ";".join(value)

        return super().db_value(value_str)

    def python_value(self, value):
        value = super().python_value(value)

        return set(value.split(";"))


class URLConfig(peewee.Model):
    """
    URLConfig model is used to dynamically configure start_urls
    """
    spider = peewee.CharField(unique=True)
    start_urls = SetField()
    created = peewee.DateTimeField(default=datetime.datetime.now)
    modified = peewee.DateTimeField()

    @classmethod
    def update_start_urls(cls, spider, start_urls, append_urls=True):
        """Update news URLs"""
        # if the database has been properly initialize the following line must succeed
        # else, a peewee.DoesNotExist will be raised
        urlconfig = cls.get(cls.spider == spider)
        start_urls = (
            set(start_urls).union(urlconfig.start_urls)
            if append_urls
            else set(start_urls)
        )
        urlconfig.start_urls = start_urls
        urlconfig.modified = datetime.datetime.now()
        urlconfig.save()

        return urlconfig

    class Meta:
        database = DB


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
        """
        Override create method to perform an update on duplicate Document.url
        """
        try:
            instance = super().create(**query)
        except peewee.IntegrityError as _:
            logging.info(
                "A document with the given URL already exists, updating record instead."
            )
            cls._meta.database.rollback()
            instance = cls.select().where(cls.url == query.pop("url")).get()
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
        date_fields = ["created", "date", "modified"]
        for field in date_fields:
            value = fields[field]
            if value and isinstance(value, str):
                fields[field] = parse_date(value)

        return fields

    @staticmethod
    def fulltext_search(
        term, kind="all", page_number=1, items_per_page=20, return_list=True
    ):
        """
        Execute a full text search query on the model and return a paginated result
        of matching records in JSON serializable format or as model instances
        """
        query = None
        if kind in ["image", "video"]:
            query = Document.fts_query_kind(term, kind)
        else:
            query = Document.fts_query_all(term)

        query = query.paginate(page_number, items_per_page)

        if return_list:
            return Document.to_list(query)

        return query

    @staticmethod
    def fts_query_all(term):
        """
        Prepare a full text search query for all possible matches

        Arguments:
            term: a string representing the search phrase

        Returns:
            peewee.SelectQuery
        """
        condition = SQL(
            "MATCH (`text`, subject, title, description, creator, publisher) AGAINST (%s IN NATURAL LANGUAGE MODE)",
            params=(term,),
        )

        return Document.select().where(condition)

    @staticmethod
    def fts_query_kind(term, kind):
        """
        Prepare a full text search query whose result have the given content type

        Arguments:
            term: a string representing the search phrase
            kind: one of (image|video), a string specifying the expected content type

        Returns:
            peewee.SelectQuery
        """
        relevance = SQL(
            (
                "MATCH (`text`, subject, title, description, creator, publisher) "
                "AGAINST (%s IN BOOLEAN MODE)"
            ),
            params=(term,),
        )

        return (
            Document.select(Document, relevance.alias("relevance"))
            .where(Document.content_type.contains(kind))
            .order_by(SQL("relevance").desc())
        )

    @staticmethod
    def to_list(query):
        """
        Given a SelectQuery, this function returns the query result as a JSON serializable list
        """
        if not isinstance(query, peewee.SelectQuery):
            error_message = (
                "`Document.to_list` received an invalid argument `query`. "
                "Got `{querytype}` instead of `peewee.SelectQuery`."
            ).format(querytype=repr(type(query)))
            logging.exception(error_message)
            raise ValueError(error_message)

        object_list = []
        for model in query:
            model_dict = {
                "url": model.url,
                "content_type": model.content_type,
                "language": model.language,
                "title": model.title,
                "subject": model.subject,
                "description": model.description,
                "creator": model.creator,
                "created": model.created.isoformat(),
                "modified": model.modified.isoformat() if model.modified else None,
            }

            object_list.append(model_dict)

        return object_list

    class Meta:
        database = DB
        constraints = [
            SQL("FULLTEXT(`text`, subject, title, description, creator, publisher)")
        ]


def initialize_database():
    Document.create_table(safe=True)
    URLConfig.create_table(safe=True)

    now = datetime.datetime.now()
    default_configs = {
        "news": {
            "start_urls": set(
                [
                    "https://www.vanguardngr.com/",
                    "http://punchng.com/",
                    "https://www.dailytrust.com.ng/",
                ]
            ),
            "modified": now,
        },
        "web": {
            "start_urls": set(
                [
                    "http://www.nairaland.com/",
                    "http://www.lindaikejisblog.com/",
                    "https://www.reddit.com/",
                    "https://news.ycombinator.com/",
                    "http://botid.org/",
                    "http://www.dirjournal.com/",
                    "http://www.jayde.com/",
                    "http://www.dmoz.org/",
                    "http://vlib.org/",
                    "http://www.business.com/",
                    "https://botw.org/",
                    "http://www.stpt.com/directory/",
                ]
            ),
            "modified": now,
        },
    }

    for (spider, defaults) in default_configs.items():
        URLConfig.get_or_create(spider=spider, defaults=defaults)


initialize_database()
