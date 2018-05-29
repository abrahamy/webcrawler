#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import os
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .spiders.news import NewsSpider
from .spiders.web import WebSpider


parser = argparse.ArgumentParser(description="Start Web Crawler", prog="start_crawl")
parser.add_argument(
    "--spider",
    metavar="-S",
    type=str,
    dest="spider",
    choices=("news", "web", "all"),
    required=True,
    help="the spider to be executed by the web crawler",
)

args = parser.parse_args()


def main():
    global args

    process = CrawlerProcess(settings=get_project_settings())

    if args.spider == "web":
        process.crawl(WebSpider)
    elif args.spider == "news":
        process.crawl(NewsSpider)
    else:
        # crawl with all spiders
        process.crawl(WebSpider)
        process.crawl(NewsSpider)

    process.start()


if __name__ == "__main__":
    main()
