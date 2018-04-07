# -*- coding: utf-8 -*-

# Scrapy settings for webcrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


BOT_NAME = 'CMSL Bot'

SPIDER_MODULES = ['webcrawler.spiders']
NEWSPIDER_MODULE = 'webcrawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'CMSL Bot (+http://www.cmsl.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 200

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.25
DOWNLOAD_TIMEOUT = 5 * 60  # 5 minutes
DOWNLOAD_MAXSIZE = 209715200  # 200MB
CONCURRENT_REQUESTS_PER_IP = 8

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'webcrawler.pipelines.ItemPipeline': 1
}

HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_GZIP = True
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'

# Database connection settings
CMSL_BOT_DATABASE = {
    'name': os.getenv('DB_NAME', 'webcrawler'),
    'user': os.getenv('DB_USER', 'webcrawler'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 3306)
}

REDIRECT_ENABLED = True

# The settings from this point to EOF are especially
# important for broad crawls
LOG_ENABLED = True
LOG_LEVEL = 'INFO'
RETRY_ENABLED = False
# REDIRECT_ENABLED = False
AJAXCRAWL_ENABLED = True
REACTOR_THREADPOOL_MAXSIZE = 50

# The next three settings ensures that the spider does
# a Breadth-First-Order (BFO) search
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
