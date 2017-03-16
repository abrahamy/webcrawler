#!/usr/bin/python3
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from webcrawler.spiders.cmsl import CmslSpider
from webcrawler.dal import Document


Document.create_table(fail_silently=True)

settings = get_project_settings()
configure_logging(settings)
crawler = CrawlerRunner(settings)


def start_crawl():
    global crawler
    deferred = crawler.crawl(CmslSpider)
    deferred.addBoth(lambda _: start_crawl())


def main():
    start_crawl()
    reactor.run()

if __name__ == '__main__':
    main()