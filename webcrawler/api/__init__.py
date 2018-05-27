# -*- coding: utf-8 -*-
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018

from flask import Flask, redirect, url_for


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load config from settings file, if it exists, when not testing
        app.config.from_object('webcrawler.settings')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from .blueprint import blueprint

    app.register_blueprint(blueprint)

    @app.route('/')
    def index():
        # redirects index route to api blueprint's base route
        return redirect(url_for('api.doc'))

    return app


app = create_app()
