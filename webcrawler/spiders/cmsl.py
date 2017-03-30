# -*- coding: utf-8 -*-
import tempfile
import mimetypes
import scrapy
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from webcrawler.items import Item


def get_start_urls():
    '''
    Get start_urls from settings and cache the result
    '''
    settings = get_project_settings()
    return settings.getlist('DEFAULT_START_URLS')


def is_mimetype(category, url):
    '''
    Return True if the url belongs to the mimetype category
    @param (category) eg. application, audio, video, etc 
    '''
    ok = False

    if url:
        mimetype, _ = mimetypes.guess_type(url)
        ok = isinstance(mimetype, str) and mimetype.startswith(category)
    
    return ok


class CmslSpider(CrawlSpider):
    name = 'cmsl'
    start_urls = get_start_urls()
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        '''
        Parse a response into an instance of webcrawler.items.Item
        '''
        try:
            fields = {
                'url': response.url,
                'links': self.extract_external_links(response),
                'media_urls': self.extract_media(response)
            }

            with tempfile.NamedTemporaryFile(delete=False) as stream:
                stream.write(response.body)
                fields['temp_filename'] = stream.name
            
            return Item(**fields)

        except OSError:
            self.logger.error(
                'Failed to save response.body to temporary file', exec_info=True
            )
    
    @staticmethod
    def extract_external_links(response):
        '''
        Extract all external links from this page
        '''
        if not isinstance(response, scrapy.http.HtmlResponse):
            return []
        
        parsed_url = urlparse(response.url)
        domain = (parsed_url.netloc,)

        link_extractor = LinkExtractor(deny_domains=domain)
        links = map(lambda link: link.url, link_extractor.extract_links(response))

        return set(links)
    
    @staticmethod
    def extract_media(response):
        '''
        Extract the urls of all media (audios, images, videos) on this page
        '''
        if not isinstance(response, scrapy.http.HtmlResponse):
            return {}
        
        # extract urls from audio, embed and video tags
        media_urls = response.css(
            'audio, audio source, embed, video, video source'
        ).xpath('@src').extract()

        # extract urls from object tag
        media_urls.extend(
            response.css('object').xpath('@data').extract()
        )

        # extract urls from param tag nested within an object tag
        media_urls.extend(
            response.css('object param[name="src"]').xpath('@value').extract()
        )

        images = response.css('img').xpath('@src').extract()
        audios = list(filter(lambda i: is_mimetype('audio', i), media_urls))
        videos = list(filter(lambda i: is_mimetype('video', i), media_urls))
        
        return {
            'images': set(images),
            'audios': set(audios),
            'videos': set(videos)
        }