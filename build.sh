#!/bin/sh

prepare_build() {
    echo "exporting required variables..."

    export RABBITMQ_PASSWORD=$(pwgen 24 1)
    export MYSQL_PASSWORD=$(pwgen 24 1)

    echo "preparing build..."
    
    cp docker-compose.sample.yml docker-compose.yml

    mkdir scrapyd
    cp scrapyd_Dockerfile scrapyd/Dockerfile
}

set -x

prepare_build

echo "starting docker-compose build..."

docker-compose --project-name '' build

echo "ce fin!"