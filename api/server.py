import hug
import validators
import falcon
from hug.types import comma_separated_list
from webcrawler.models import Document, Job


api = hug.API(__name__)


@hug.get('/search', api=api)
@hug.post('/search', api=api)
def search(query: hug.types.text, page: hug.types.number = 1, items: hug.types.number = 20):
    '''
    Search the database of crawled data

    Arguments:
        query: the text to search for
        page: the current page of data to be returned
        items: the number of items per page

    Returns:
        list of JSON objects
    '''
    return Document.fulltext_search(query, page_number=page, items_per_page=items)


def _validate_urls(urls):
    '''
    Takes a list of strings representing urls and validates them
    @see hug.types.comma_separated_list

    Returns:
        (set(valid_urls), set(invalid_urls))
    '''
    valid_urls = filter(validators.url, urls)
    invalid_urls = filter(lambda u: not validators.url(u), urls)

    return set(valid_urls), set(invalid_urls)


@hug.post('/updateNewsUrls', api=api)
def update_news_crawler_settings(
        news_urls: hug.types.comma_separated_list, append_urls: hug.types.boolean=False):
    '''
    Update the settings for the news crawler

    Parameters:
        news_urls: a comma separated list valid URLs.
        append_urls: append or replace existing URLs? Default: False (i.e. replace)

    Returns:
        JSON object
    '''
    valid_urls, invalid_urls = _validate_urls(news_urls)

    if not len(valid_urls):
        error_msg = '`news_urls` must be a comma separated string of valid URLs.'
        raise falcon.HTTPBadRequest(error_msg)

    Job.update_news_urls(news_urls, append_urls=append_urls)

    reply = {
        'status': 'News crawler settings successfully updated!'
    }
    if len(invalid_urls):
        reply['status'] = 'Partially updated news URLs. Check the `data` field for invalid URLs.'
        reply['data'] = ','.join(invalid_urls)

    return reply


application = api.http.server()
