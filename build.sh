#!/bin/sh
set -x

export RABBITMQ_HOST=rabbitmq-broker
export RABBITMQ_PASSWORD=$(pwgen 24 1)
export MYSQL_PASSWORD=$(pwgen 24 1)

cp docker-compose.sample.yml docker-compose.yml

mkdir scrapyd
cp scrapyd_Dockerfile scrapyd/Dockerfile

docker-compose --project-name '' build