import tempfile
from behave import *
from webcrawler.items import Item, Parsed
from webcrawler.pipelines import ContentParser
from webcrawler.spiders.cmsl import CmslSpider


ITEM_URL = 'http://www.example.com/'
ITEM_TEXT = b'''
<!doctype html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
    <head>
        <title>reddit: the front page of the internet</title>
        <meta name="keywords" content=" reddit, reddit.com, vote, comment, submit " />
        <meta name="description" content="reddit: the front page of the internet" />
        <meta name="referrer" content="always">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link type="application/opensearchdescription+xml" rel="search" href="/static/opensearch.xml"/>
        <link rel="canonical" href="https://www.reddit.com/" />
        <link rel="alternate" media="only screen and (max-width: 640px)" href="https://m.reddit.com/" />
        <meta name="viewport" content="width=1024">
    </head>
    <body>
        <h1>Hello, World!</h1>
        <ul>
            <li><a href="http://www.example.com/page1">Internal Link</a></li>
            <li><a href="/page2">Another Internal Link</a></li>
            <li><a href="http://www.ext.com/extpage">External Link</a></li>
            <li><a href="http://ext.com/that/page">Another External Link</a></li>
        </ul>
    </body>
</html>
'''
ITEM_LINKS = [
    'http://www.ext.com/extpage',
    'http://www.ext.com/that/page'
]


@given('a webcrawler.pipelines.ContentParser, webcrawler.items.Item and a webcrawler.spiders.cmsl.CmslSpider')
def step_impl(context):
    '''
    Note: this step requires that a tika server instance be running on localhost
    '''
    context.parser = ContentParser()
    context.spider = CmslSpider()

    with tempfile.NamedTemporaryFile(delete=False) as stream:
        stream.write(ITEM_TEXT)

        context.item = Item(
            url=ITEM_URL, links=ITEM_LINKS, temp_filename=stream.name
        )


@when('process_item is invoked on ContentParser with Item and CmslSpider')
def step_impl(context):
    context.process_item_result = context.parser.process_item(context.item, context.spider)


@then('it should return a webcrawler.items.Parsed')
def step_impl(context):
    assert(type(context.process_item_result)==Parsed)


@given('a webcrawler.pipelines.ContentParser, an invalid item and a webcrawler.spiders.cmsl.CmslSpider')
def step_impl(context):
    context.parser = ContentParser()
    context.spider = CmslSpider()
    context.invalid_item = ('Hello, World!',)


@when('process_item is invoked on ContentParser with the item and CmslSpider')
def step_impl(context):
    context.process_item_result_invalid_item = context.parser.process_item(
        context.invalid_item, context.spider
    )


@then('it should return the same item unchanged')
def step_impl(context):
    assert(context.invalid_item == context.process_item_result_invalid_item)