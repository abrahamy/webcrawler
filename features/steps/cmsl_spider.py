from behave import *
from urllib.parse import urlparse
from scrapy.http import Request, Response
from webcrawler.items import Item
from webcrawler.spiders.cmsl import CmslSpider

URL = 'http://www.example.com/'
RESPONSE_BODY = b'''
<html lang="en">
    <head>
        <title>Sample Page</title>
    </head>
    <body>
        <ul>
            <li><a href="http://www.example.com/page1">Internal Link</a></li>
            <li><a href="/page2">Another Internal Link</a></li>
            <li><a href="http://www.ext.com/extpage">External Link</a></li>
            <li><a href="http://ext.com/that/page">Another External Link</a></li>
        </ul>
    </body>
</html>
'''

@given('a webcrawler.spiders.cmsl.CmslSpider and a scrapy.http.Response')
def step_impl(context):
    request = Request(URL)

    context.response = Response(URL, body=RESPONSE_BODY, request=request)
    context.spider = CmslSpider()


@when('parse_item method of CmslSpider is invoked with a response')
def step_impl(context):
    context.parse_item_result = context.spider.parse_item(context.response)


@then('it should return a webcrawler.items.Item')
def step_impl(context):
    assert(type(context.parse_item_result)==Item)


@when('extract_external_links is invoked with a response')
def step_impl(context):
    context.extract_external_links_result = context.spider.extract_external_links(context.response)


@then('it should return a list of urls')
def step_impl(context):
    assert(type(context.extract_external_links_result)==list)
    assert(all([type(url) is str for url in context.extract_external_links_result]))


@then('the urls should be external urls')
def step_impl(context):
    extracted_urls = context.extract_external_links_result
    same_domain = filter(lambda url: urlparse(url).netloc.contains('example.com'))

    assert(len(extracted_urls)==2)
    assert(len(same_domain)==0)
