#!/bin/sh
uwsgi --http 0.0.0.0:80 --uid uwsgi \
      --plugins python3 --protocol uwsgi
      --logto logs/uWSGI.log
      --wsgi "server:__hug_wsgi__"