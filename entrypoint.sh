#!/bin/bash

# wait for the database and tika server to come online
sleep 40

/usr/bin/supervisord -c /supervisord.conf