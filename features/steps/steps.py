import os
from behave import *
from scrapy.http import Response
from webcrawler.pipelines import ContentParser
from webcrawler.items import Raw, CrawlData
from webcrawler.spiders.cmsl import CmslSpider


fixture_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')


@given('a CmslSpider and Response')
def step_impl(context):
    context.spider = CmslSpider()

    response_file = os.path.join(fixture_dir, 'reddit.com.html')
    with open(response_file, 'r+b') as rf:
        body = rf.read()
    
    context.response = Response(url='http://www.reddit.com/', body=body)


@when('CmslSpider.parse_item is called')
def step_impl(context):
    context.item = context.spider.parse_item(context.response)


@then('it should return a Raw item')
def step_impl(context):
    assert(type(context.item)==Raw)


@given('a ContentParser')
def step_impl(context):
    context.parser = ContentParser()


@when('ContentParser.process_item is called')
def step_impl(context):
    context.data = context.parser.process_item(context.item, context.spider)


@then('it should return a CrawlData item')
def step_impl(context):
    assert(type(context.data)==CrawlData)