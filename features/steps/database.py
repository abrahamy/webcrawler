from behave import *
from dateutil.parser import parse
from scrapy.utils.project import get_project_settings
from webcrawler.items import Document, Search


database = Document._meta.database


@given('that new document has been added')
def step_impl(context):
    data = {
        'url': 'http://www.example.com/',
        'created': parse('2016-10-19T15:10:17')
    }
    with database.atomic():
        context.doc = Document.create(**data)


@when('we query the Document model with it\'s id')
def step_impl(context):
    where = (Document.id == context.doc.id)
    context.result = Document.select().where(where).get()


@then('it should return an instance of Document')
def step_impl(context):
    assert(isinstance(context.result, Document))


@given('that a new document has been added')
def step_impl(context):
    data = {
        'url': 'http://www.example2.com/',
        'created': parse('2016-10-19T15:10:17')
    }
    with database.atomic():
        context.doc = Document.create(**data)


@when('we query the Search model with it\'s id')
def step_impl(context):
    where = (Search.document == context.doc)
    context.result = Search.select().where(where).get()


@then('it should return an instance of Search')
def step_impl(context):
    assert(isinstance(context.result, Search))