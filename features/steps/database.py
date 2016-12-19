from behave import *
from scrapy.utils.project import get_project_settings
from webcrawler.items import Document, Search


@given('that new document has been added')
def step_impl(context):
    pass


@when('we query the Document model with it\'s id')
def step_impl(context):
    pass


@then('it should return an instance of Document')
def step_impl(context):
    assert(True, False)


@given('that a new document has been added')
def step_impl(context):
    pass


@when('we query the Search model with it\'s id')
def step_impl(context):
    pass


@then('it should return an instance of Search')
def step_impl(context):
    assert(True, False)