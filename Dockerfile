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
    rm -rf /usr/src/* && mkdir -p /var/log/webcrawler && \
    touch /var/log/webcrawler/{news,web}.log && \
    chmod ugo+rwX /var/log/webcrawler && \
    chmod ugo+rw /var/log/webcrawler/{news,web}.log

# Install API service
COPY api/requirements.txt /usr/src/
RUN pip install --no-cache-dir -r /usr/src/requirements.txt && \
    rm /usr/src/requirements.txt && useradd -ms /bin/bash api
USER api
COPY api/* /home/api/
COPY webcrawler /home/api/webcrawler
WORKDIR /home/api
VOLUME [ "/home/api/logs" ]

USER root

# Copy supervisord configs
COPY supervisord.conf /supervisord.conf
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]