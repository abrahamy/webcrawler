#!/usr/bin/env bash

cd /home/api

# wait for 3 minutes for mysql and rabbitmq to come up
sleep 180

if [ -f celery.pid ] 
    rm celery.pid
fi
celery -A tasks worker --loglevel=info --pidfile=celery.pid

# Start API server
uwsgi --yaml uwsgi.yml