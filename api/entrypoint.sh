#!/usr/bin/env bash

cd /home/api

# wait for 3 minutes for mysql and rabbitmq to come up
sleep 90

# Start API server
uwsgi --yaml uwsgi.yml