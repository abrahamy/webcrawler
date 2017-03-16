#!/usr/bin/python3
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from webcrawler.spiders.cmsl import CmslSpider
from webcrawler.dal import Document


Document.create_table(fail_silently=True)
crawler = CrawlerRunner(get_project_settings())


def start_crawl():
    global crawler
    deferred = crawler.crawl(CmslSpider)
    deferred.addBoth(lambda _: start_crawl())


start_crawl()
reactor.run()