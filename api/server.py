import hug
from webcrawler.dal import Document


@hug.get
@hug.post
def search(query, page=1, items=20):
    '''Search the database of crawled data'''
    return Document.fulltext_search(query, page_number=page, items_per_page=items)


@hug.post
def update_news_urls(urls):
    '''Replace existing news urls with the new ones'''
    pass


@hug.post
def update_news_crawler_settings(settings):
    '''Update the settings for the news crawler'''
    pass
