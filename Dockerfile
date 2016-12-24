FROM        python:alpine
MAINTAINER  aaondowasey@gmail.com

ENV         TIKA_CLIENT_ONLY True

COPY        . /usr/src/webcrawler
WORKDIR     /usr/src/webcrawler
RUN         apk add --no-cache postgresql-dev libffi-dev
RUN         pip3 install --no-cache-dir --upgrade \
                --force-reinstall -r requirements.txt
CMD         ["scrapy", "crawl", "cmsl"]


