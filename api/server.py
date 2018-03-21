import hug
try:
    # Wrapped in a try-catch because when using docker-compose the database container
    # may not be ready when this import is executed
    from webcrawler.dal import Document
except Exception as _:
    Document = None


@hug.get
@hug.post
def search(query, page=1, items=20):
    '''Search the database of crawled data'''
    if not Document:
        from webcrawler.dal import Document
    return Document.fulltext_search(query, page_number=page, items_per_page=items)


@hug.post
def update_news_urls(urls):
    '''Replace existing news urls with the new ones'''
    pass


@hug.post
def update_news_crawler_settings(settings):
    '''Update the settings for the news crawler'''
    pass


application = hug.API(__name__).http.server()
