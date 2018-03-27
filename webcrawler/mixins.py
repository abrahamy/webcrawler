# -*- coding: utf-8 -*-
import os
import scrapy
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor


IMAGE_EXTENSIONS = [
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',
]

AUDIO_EXTENSIONS = [
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',
]

VIDEO_EXTENSIONS = [
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a', 'm4v',
]

DOCUMENT_EXTENSIONS = [
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
    'odp', 'pdf',
]


link_extractor = LinkExtractor(
    tags=('a', 'area', 'img', 'source', 'track', 'embed'),
    attrs=('href', 'src'), deny_extensions=()
)


def _get_ext(link: scrapy.link.Link):
    '''Get the link's extension'''
    return os.path.splitext(link.url)[1].replace('.', '')


class LinkExtractionMixin(object):
    '''
    LinkExtractionMixin implements utility functions for extracting different kinds of links
    '''

    __extracted_links = None

    def __extract_all_links(self, response: scrapy.http.Response):
        '''Extracts all links and caches them an instance attribute'''
        if self.__extracted_links:
            return self.__extracted_links

        if not isinstance(response, scrapy.http.HtmlResponse):
            return []

        link_extractor = LinkExtractor(
            tags=('a', 'area', 'img', 'source', 'track', 'embed'),
            attrs=('href', 'src'), deny_extensions=()
        )
        self.__extracted_links = link_extractor.extract_links(response)

        return self.__extracted_links

    def __filter_links_by_extension(self, response: scrapy.http.Response, extensions):
        '''Returns all links whose extension is in `extensions`'''
        links = self.__extract_all_links(response)
        return [link for link in links if _get_ext(link) in extensions]

    def extract_image_links(self, response: scrapy.http.Response):
        '''Extracts links to all images on a given page'''
        return self.__filter_links_by_extension(response, IMAGE_EXTENSIONS)

    def extract_audio_links(self, response: scrapy.http.Response):
        '''Extracts links to all audio files on a given page'''
        return self.__filter_links_by_extension(response, AUDIO_EXTENSIONS)

    def extract_video_links(self, response: scrapy.http.Response):
        '''extracts links to all video files on a given page'''
        return self.__filter_links_by_extension(response, VIDEO_EXTENSIONS)

    def extract_document_links(self, response: scrapy.http.Response):
        '''Extracts links to all documents on a given page'''
        return self.__filter_links_by_extension(response, DOCUMENT_EXTENSIONS)

    def extract_external_urls(self, response: scrapy.http.Response):
        '''Extract all external urls from this page'''
        if not isinstance(response, scrapy.http.HtmlResponse):
            return []

        parsed_url = urlparse(response.url)
        domain = (parsed_url.netloc,)

        _link_extractor = LinkExtractor(deny_domains=domain)
        urls = map(lambda link: link.url,
                   _link_extractor.extract_links(response))

        return set(urls)
