# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018

FROM python:3.6

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

# Install Supervisord
RUN apt-get update \
    && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/* && \
    mkdir /opt/supervisor

# Install webcrawler
COPY . /usr/src/
WORKDIR /usr/src
RUN python setup.py bdist_wheel && \
    pip install --no-cache-dir dist/webcrawler*.whl && \
    rm -rf /usr/src/* && \
    useradd -ms /bin/bash webcrawler

WORKDIR /home/webcrawler
VOLUME [ "/home/webcrawler/logs" ]

# Copy config files
COPY config/supervisord.conf /supervisord.conf
COPY config/uwsgi.yml /uwsgi.yml
COPY config/entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]