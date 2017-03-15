#!/usr/bin/python3
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webcrawler.spiders.cmsl import CmslSpider
from webcrawler.items import initialize_database
#<-- Remove
import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
# --/>

initialize_database()

crawler = CrawlerProcess(get_project_settings())

crawler.crawl(CmslSpider)
crawler.start()