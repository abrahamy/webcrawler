# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import hug
import validators
import falcon
from hug.types import comma_separated_list
from webcrawler.models import Document, URLConfig


api = hug.API(__name__)


@hug.get('/search', api=api)
@hug.post('/search', api=api)
def search(
        query: hug.types.text,
        kind: hug.types.one_of(['all', 'image', 'video']) = 'all',
        page: hug.types.number = 1, items: hug.types.number = 20):
    '''
    Search the database of crawled data

    Arguments:
        query: the text to search for
        t: the type of content to be returned
        page: the current page of data to be returned
        items: the number of items per page

    Returns:
        list of JSON objects
    '''
    return Document.fulltext_search(query, kind=kind, page_number=page, items_per_page=items)


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


@hug.post('/updateUrls', api=api)
def update_urls(
        spider: hug.types.one_of(['news', 'web']),
        start_urls: hug.types.comma_separated_list,
        append_urls: hug.types.boolean=False):
    '''
    Update URLs for the web crawler

    Parameters:
        spider: the spider whose URLs are to be updated
        start_urls: a comma separated list of valid URLs.
        append_urls: append or replace existing URLs? Default: False (i.e. replace)

    Returns:
        JSON
    '''
    valid_urls, invalid_urls = _validate_urls(start_urls)

    if not len(valid_urls):
        error_msg = '`start_urls` must be a comma separated string of valid URLs.'
        raise falcon.HTTPBadRequest(error_msg)

    URLConfig.update_start_urls(spider, start_urls, append_urls=append_urls)

    reply = {
        'status': 'News crawler settings successfully updated!'
    }
    if len(invalid_urls):
        reply['status'] = 'Partially updated news URLs. Check the `data` field for invalid URLs.'
        reply['data'] = ','.join(invalid_urls)

    return reply


application = api.http.server()
