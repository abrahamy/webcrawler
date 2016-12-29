FROM        alpine
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
                && apk add --no-cache \
                    ca-certificates \
                    libpq \
                    python3 \
                    py-pip \
                && apk add --no-cache --virtual buildDeps \
                    python3-dev \
                    libpq-dev \
                    libffi-dev \
                    postgresql-dev \
                    build-base \
                && python3 -m pip install --no-cache-dir --upgrade \
                    --force-reinstall -r requirements.txt \
                && apk del buildDeps

VOLUME      ["/var/log/cmslbot"]

# expose required ports
# 80: HTTP port for serving REST API using uWSGI
# 6800: Telnet control port for scrapy
# 9191: uWSGI stats port
EXPOSE      80 6800 9191

CMD             uwsgi uwsgi.yml && scrapy crawl cmsl
