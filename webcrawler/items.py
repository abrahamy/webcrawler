# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import base64, uuid, scrapy
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import sessionmaker


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


Base = declarative_base()


class Archive(Base):
    __tablename__ = 'archive'

    id = Column(String(25), primary_key=True)
    url = Column(String(255))
    data = Column(Text)
    meta = Column(MutableDict.as_mutable(HSTORE))

    def __repr__(self):
        return '<Archive(id="{}", url="{}")>'.format(self.id, self.url)
    
    def save(self):
        '''
        Stores this instance of the model in the database
        '''
        session = self.create_session()
        session.add(self)
        session.commit()
        return self
    
    def create_session(self):
        '''
        Creates and returns database session object.
        Side Effect: creates the table schema if not exists
        '''
        engine = self.metadata.bind

        if not engine:
            db_uri = get_project_settings().get('SQL_ALCHEMY_URI')
            engine = create_engine(db_uri)

            engine.execute('CREATE EXTENSION IF NOT EXISTS hstore;')
            self.__table__.create(engine, checkfirst=True)
        
        Session = sessionmaker(engine)
        return Session()

    @staticmethod
    def gen_pk():
        pk = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        return str(pk.replace(b'=', b''))