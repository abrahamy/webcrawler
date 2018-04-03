#!/usr/bin/env python3
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webcrawler.spiders.news import NewsSpider
from webcrawler.spiders.web import WebSpider


parser = argparse.ArgumentParser(
    description='Start Web Crawler', prog='start_crawl')
parser.add_argument(
    '--spider', metavar='S', type=str, dest='spider', choices=('news', 'web', 'all'),
    required=True, help='the spider to be executed by the web crawler'
)

args = parser.parse_args()


def main():
    global args

    process = CrawlerProcess(settings=get_project_settings())

    if args.spider == 'web':
        process.crawl(WebSpider)
    elif args.spider == 'news':
        process.crawl(NewsSpider)
    else:
        # crawl with all spiders
        process.crawl(WebSpider)
        process.crawl(NewsSpider)

    process.start()


if __name__ == '__main__':
    main()
