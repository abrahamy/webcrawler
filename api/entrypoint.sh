#!/bin/sh

# Wait for database container to be ready
wait-for-it ${MYSQL_DATABASE_HOST}:3306 -t 40

# Wait for rabbitmq container to be ready
wait-for-it ${RABBITMQ_HOST}:5672 -t 20

# Start API server
/usr/local/bin/uwsgi --yaml uwsgi.yml