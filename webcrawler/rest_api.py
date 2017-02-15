'''A RESTful API for searching indexed documents'''
import hug
from webcrawler.items import Document


@hug.get(response_headers={'Access-Control-Allow-Origin': '*'})
def search(term: hug.types.text, page: hug.types.number=1, items: hug.types.number=20):
    '''
    Search for documents that match the given term
    '''
    return Document.fulltext_search(term, page_number=page, items_per_page=items)