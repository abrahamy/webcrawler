import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import endpoints, reactor
from twisted.web import http, resource, server
from webcrawler.spiders.cmsl import CmslSpider
from webcrawler.items import Document


class SearchAPI(resource.Resource):
    isLeaf = True

    class SearchTerm(object):
        def __init__(self, term, page_number=1, items_per_page=20):
            self.term = term
            self.page_number = page_number
            self.items_per_page = items_per_page

    def render_GET(self, request):
        search = self.get_search_term(request)

        if not search.term:
            request.setResponseCode(http.BAD_REQUEST)
            return http.RESPONSES[http.BAD_REQUEST]
        
        search_results = Document.fulltext_search(
            search.term, search.page_number, search.items_per_page
        )

        if not len(search_results):
            request.setResponseCode(404)
            return http.RESPONSES[http.NOT_FOUND]
        
        request.setHeader('Content-Type', 'application/json')
        return bytes(search_results, 'utf-8')
    
    @staticmethod
    def get_param_key(key, request):
        '''
        Get the value of a given HTTP GET parameter
        '''
        param = request.args.get(key)
        return param[0] if param and len(param) else None
    
    @classmethod
    def get_search_term(cls, request):
        '''
        Get the SearchTerm instance for this request
        '''
        term = cls.get_param_key('q', request)
        kwargs = {
            'page_number': cls.get_param_key('p') or 1,
            'items_per_page': cls.get_param_key('n') or 20
        }

        return cls.SearchTerm(term, **kwargs)
    
    @classmethod
    def configure_site(cls):
        rsrc = cls()
        rsrc_gzipped = resource.EncodingResourceWrapper(rsrc, [server.GzipEncoderFactory()])
        site = server.Site(rsrc_gzipped)
        endpoint = endpoints.TCP4ServerEndpoint(reactor, 8000)
        endpoint.listen(site)


runner = CrawlerRunner(get_project_settings())
runner.crawl(CmslSpider)
SearchAPI.configure_site()

reactor.run()