FROM python:3.6

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

# Install Supervisord
RUN apt-get update \
    && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install webcrawler
COPY . /usr/src/
WORKDIR /usr/src
RUN python setup.py install && rm -rf /usr/src/*

# Install API service
RUN useradd -ms /bin/bash api
USER api
COPY api/* /home/api
COPY webcrawler /home/api/webcrawler
WORKDIR /home/api
RUN pip install --no-cache-dir -r requirements.txt
VOLUME [ "/home/api/logs" ]
# Start API server
CMD [ "/usr/local/bin/uwsgi", "--yaml", "uwsgi.yml" ]

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT [ "/usr/bin/supervisord" ]