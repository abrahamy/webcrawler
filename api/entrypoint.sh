#!/usr/bin/env bash

cd /home/api

# Wait for database container to be ready
. /wait-for-it.sh ${MYSQL_DATABASE_HOST}:3306 -t 40

# Wait for rabbitmq container to be ready
. /wait-for-it.sh ${RABBITMQ_HOST}:5672 -t 20

# Start API server
uwsgi --yaml uwsgi.yml