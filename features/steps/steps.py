import os
from behave import *
from scrapy.http import Response
from webcrawler.pipelines import TikaParser
from webcrawler.items import Raw, Metadata
from webcrawler.spiders.cmsl import CmslSpider


fixture_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')


@given('an instance of TikaParser pipeline, a Raw item and a CmslSpider')
def step_impl(context):
    context.pipeline = TikaParser()
    context.spider = CmslSpider()

    response_file = os.path.join(fixture_dir, 'reddit.com.html')
    with open(response_file, 'r+b') as rf:
        body = rf.read() or b''
    
    response = Response(url='http://www.reddit.com/', body=body)
    context.item = context.spider.parse_item(response)


@when('the process_item is called with a Raw item and a CmslSpider')
def step_impl(context):
    context.result = context.pipeline.process_item(context.item, context.spider)


@then('it should return a Metadata item')
def step_impl(context):
    assert(type(context.item)==Raw)
    assert(type(context.result)==Metadata)