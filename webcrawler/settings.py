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

CMSL_PROJECT_ROOT = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)

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
DOWNLOAD_TIMEOUT = 300 #prod=15
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 8
# CONCURRENT_REQUESTS_PER_IP = 0

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'webcrawler.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'webcrawler.pipelines.ContentParser': 300,
    'webcrawler.pipelines.FTSIndexer': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3 * 60 * 60 # prod=24 * 60 * 60 # cache for 24 hours
HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_GZIP = True
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'

# Database connection settings
CMSL_BOT_DATABASE = {
    'name': 'webcrawler',
    'user': 'webcrawler',
    'password': 'super-secret-password',
    'host': 'localhost',
    'port': 5432
}

DEFAULT_START_URLS = [
    'http://www.nairaland.com/',
    'http://www.lindaikejisblog.com/',
    'https://www.reddit.com/',
    'https://news.ycombinator.com/',
    'http://botid.org/',
    'http://www.dirjournal.com/',
    'http://www.jayde.com/',
    'http://www.dmoz.org/',
    'http://vlib.org/',
    'http://www.business.com/',
    'https://botw.org/',
    'http://www.stpt.com/directory/',
]

# The settings from this point to EOF are especially
# important for broad crawls
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(CMSL_PROJECT_ROOT, 'logs', 'spider.log')
RETRY_ENABLED = False
REDIRECT_ENABLED = True # prod=False
AJAXCRAWL_ENABLED = True
REACTOR_THREADPOOL_MAXSIZE = 50

# The next three settings ensures that the spider does
# a Breadth-First-Order (BFO) search
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'