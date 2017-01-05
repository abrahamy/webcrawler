FROM        python:3.5
MAINTAINER  aaondowasey@gmail.com

LABEL       Author      = "Abraham Aondowase Yusuf"\
            Project     = "CMSL Bot"\
            Version     = "1.0.0"\
            Copyright   = "2016, Abraham Aondowase Yusuf"

ENV         TIKA_CLIENT_ONLY True \
            LANG C.UTF-8

COPY        . /usr/src/webcrawler
WORKDIR     /usr/src/webcrawler

RUN         set -ex \
                && apt-get update \
                && apt-get install -y --no-install-recommends \
                    libpq5 libffi-dev libpq-dev \
                && pip3 install --no-cache-dir --upgrade \
                    --force-reinstall -r requirements.txt \
                && apt-get purge -y --auto-remove libffi-dev libpq-dev \
                && rm -rf /var/cache/apt/*

VOLUME      ["/var/log/cmslbot"]

# expose required ports
# 80: HTTP port for serving REST API using uWSGI
# 6800: Telnet control port for scrapy
# 9191: uWSGI stats port
EXPOSE      80 6800 9191

CMD             uwsgi uwsgi.yml && scrapy crawl cmsl
