# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import functools
import validators
from flask import Blueprint
from flask_restplus import Api, fields, Resource
from webcrawler.models import Document, URLConfig


blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(blueprint, description="Web Crawler API")

search_parser = api.parser()
search_parser.add_argument(
    "text", required=True, help="The text to be searched", location=("args",), trim=True
)
search_parser.add_argument(
    "kind",
    choices=("all", "image", "video"),
    default="all",
    help="Type of search to be performed, possible values are `all`, `image`, `video`",
    location=("args",),
    trim=True,
)
search_parser.add_argument(
    "page_number",
    default=1,
    help="The page of result to be returned",
    location=("args",),
    type=int,
)
search_parser.add_argument(
    "items_per_page",
    default=20,
    help="The number of items per page",
    location=("args",),
    type=int,
)

url_model = api.model(
    "UpdateURLs",
    {
        "spider": fields.String(
            required=True,
            description=(
                "Specifies the name of the spider to "
                "update, possible values are `news`, `web`"
            ),
        ),
        "urls": fields.String(
            required=True,
            description=(
                "comma separated list of valid urls, i.e. urls "
                "must start with either http:// or https://"
            ),
        ),
        "mode": fields.String(
            default="replace",
            description="update strategy, possible values are `append`, `replace`",
        ),
    },
)


def validate_urls(urls):
    """
    Takes a list of strings representing urls and validates them
    Returns:
        (set(valid_urls), set(invalid_urls))
    """
    valid_urls = filter(validators.url, urls)
    invalid_urls = filter(lambda u: not validators.url(u), urls)

    return set(valid_urls), set(invalid_urls)


def transactional(f):
    """Wraps database operations in a transaction"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        db = Document._meta.database
        with db.atomic():
            return f(*args, **kwargs)

    return wrapper


@api.route("/search")
class Search(Resource):
    """Search Resource"""

    @api.doc("Search", responses={200: "Search Completed!"})
    @api.expect(search_parser)
    @transactional
    def get(self):
        """Search Indexed Data"""
        query = search_parser.parse_args(strict=True)
        kwargs = {
            "kind": query.kind,
            "page_number": query.page_number,
            "items_per_page": query.items_per_page,
        }
        search_result = Document.fulltext_search(query.text, **kwargs)
        return search_result, 200


@api.route("/spider")
class Spider(Resource):
    """Spider Resource"""

    @api.doc("Spider", responses={200: "Success"})
    @transactional
    def get(self):
        """List all spiders"""
        spiders = []
        for spider in URLConfig.select():
            spiders.append(
                {
                    "spider": spider.spider,
                    "start_urls": list(spider.start_urls),
                    "created": spider.created.isoformat(),
                    "modified": spider.modified.isoformat(),
                }
            )
        return spiders, 200

    @api.doc(
        "Spider", responses={200: "Success", 206: "Partial Update", 400: "Bad Request"}
    )
    @api.expect(url_model)
    @transactional
    def post(self):
        """Update URLs and restart the spider"""
        mode = api.payload.pop("mode", "replace")
        spider = api.payload.pop("spider")
        start_urls = api.payload.pop("urls").split(",")

        errors = {}
        if not mode in ["append", "replace"]:
            errors["mode"] = "`mode` must be one of `append`, `replace`"

        if spider not in ["news", "web"]:
            errors["spider"] = "`spider` must be one of `news`, `web`"

        valid_urls, invalid_urls = validate_urls(start_urls)

        if not len(valid_urls):
            errors[
                "urls"
            ] = "`urls` must be a non empty comma separated list of valid URLs."

        if len(errors.keys()):
            return errors, 400

        URLConfig.update_start_urls(
            spider, start_urls, append_urls=True if mode is "append" else False
        )

        if not len(invalid_urls):
            return "URLs successfully updated!", 200

        msg = "URLs partially updated. The following URLs were invalid: `{}`.".format(
            ", ".join(invalid_urls)
        )
        return msg, 206
