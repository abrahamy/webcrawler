#!/usr/bin/python3
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webcrawler.spiders.cmsl import CmslSpider

crawler = CrawlerProcess(get_project_settings())

crawler.crawl(CmslSpider)
crawler.start()