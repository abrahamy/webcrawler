#!/bin/sh
uwsgi --http 0.0.0.0:80 --wsgi-file server.py --callable __hug_wsgi__