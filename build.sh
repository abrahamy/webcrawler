#!/bin/sh

prepare_build() {
    echo "preparing build..."
    echo "generating mysql password..."
    
    local mysql_password=$(pwgen 24 1)
    local placeholder=some-random-gibberish

    echo "mysql password generated! password is: $mysql_password"
    echo "replacing password placeholder with new password..."

    sed -i '' s/$placeholder/$mysql_password/g docker-compose.yml
}

set -x

prepare_build

echo "starting docker-compose build..."

docker-compose --project-name '' build

echo "ce fin!"