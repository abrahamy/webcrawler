import hug
import validators
from hug.types import comma_separated_list, DelimitedList
from webcrawler.models import Document, NewsConfig


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

    Example:
        >>> search('Nigerian Fashion', page=1, items=2)
        [
            {
                "url": "http://www.lindaikejisblog.com/fashion",
                "content_type": "text/html",
                "language": "en",
                "title": "Get the latest fashion news!",
                "subject": "Fashion",
                "description": "",
                "creator": "Linda Ikeji",
                "created": "01-01-2017 20:20:47",
                "modified": "01-01-2017 20:20:47"
            },
            ...
        ]
    '''
    return Document.fulltext_search(query, page_number=page, items_per_page=items)


def _validate_urls(urls):
    '''
    Takes a list of strings representing urls and validates them
    @see hug.types.DelimitedList

    Returns:
        (set(valid_urls), set(invalid_urls))
    '''
    valid_urls = filter(validators.url, urls)
    invalid_urls = filter(lambda u: not validators.url(u), urls)

    return set(valid_urls), set(invalid_urls)


_news_urls_type = hug.types.multi([
    comma_separated_list, DelimitedList(using='\n'), DelimitedList(using=';')
])


@hug.post('/updateNewsSettings', api=api)
def update_news_crawler_settings(
        news_urls: _news_urls_type,
        restart_interval: hug.types.float_number=2.0,
        append_urls: hug.types.greater_than=False):
    '''
    Update the settings for the news crawler

    Parameters:
        news_urls: a delimited string of valid URLs. The URLs can be delimited with commas, newlines or semicolons.
        restart_interval: interval in hours for reindexing the news URLs, fractions allowed. Must be > 0. Default: every 2 hours
        append_urls: append or replace existing URLs? Default: False (i.e. replace)

    Returns:
        JSON object

    Example:
        >>> updateNewsSettings('www.lindaikejisblog.com,www.google', restart_interval=2, append_urls=False)
        {
            "status": "Partially updated news URLs. Check the `data` field for invalid URLs.",
            "data": "www.google"
        }
        >>> updateNewsSettings('www.lindaikejisblog.com,www.nairaland.com', restart_interval=2, append_urls=False)
        {
            "status": "News crawler settings successfully updated!"
        }
    '''
    if restart_interval < 0.5 or restart_interval > 24:
        raise hug.exceptions.InvalidTypeData(
            '`restart_interval` should be a decimal number between 0.5 and 24 (inclusive)')

    valid_urls, invalid_urls = _validate_urls(news_urls)

    if not len(valid_urls):
        error_msg = (
            '`news_urls` must be a delimited string of valid URLs. '
            'Allowed delimiters: comma, newline and semicolon.'
        )
        raise hug.exceptions.InvalidTypeData(error_msg)

    NewsConfig.create_or_update_news_config(
        news_urls, restart_interval=restart_interval, append_urls=append_urls)  # @todo: trigger NewsSpider restart

    reply = {
        'status': 'News crawler settings successfully updated!'
    }
    if len(invalid_urls):
        reply['status'] = 'Partially updated news URLs. Check the `data` field for invalid URLs.'
        reply['data'] = ','.join(invalid_urls)

    return reply


application = api.http.server()
