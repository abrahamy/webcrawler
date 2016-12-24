FROM        python:alpine
MAINTAINER  aaondowasey@gmail.com

LABEL       Author      = "Abraham Aondowase Yusuf"\
            Project     = "CMSL Bot"\
            Version     = "1.0.0"\
            Copyright   = "2016, Abraham Aondowase Yusuf"

ENV         TIKA_CLIENT_ONLY True

VOLUME      ["/var/log/cmslbot"]

EXPOSE      80 6800

COPY        . /usr/src/webcrawler
WORKDIR     /usr/src/webcrawler

RUN         apk add --no-cache postgresql-dev libffi-dev
RUN         pip3 install --no-cache-dir --upgrade \
                --force-reinstall -r requirements.txt

ENTRYPOINT  ["scrapy", "crawl", "cmsl"]


