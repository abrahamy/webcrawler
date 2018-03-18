#!/bin/sh

# the mysql container does not start fast enough despite adding a depends_on in docker-compose.yml
sleep 90

. /usr/local/bin/crawl $1