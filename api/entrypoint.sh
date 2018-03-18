#!/bin/sh
uwsgi --http 0.0.0.0:80 --wsgi-file __main__.py --callable __hug_wsgi__