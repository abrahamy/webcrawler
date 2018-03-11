# Containerize App
FROM python:stretch

LABEL Author=Abraham\ Yusuf\ <aaondowasey@gmail.com> \
    Client=Cubic\ Multi\ Services\ Limited

COPY . /usr/src/webcrawler
WORKDIR /usr/src/webcrawler
RUN pip install --no-cache-dir wheel && \
    python setup.py bdist_wheel && \
    cp dist/webcrawler*.whl ../ && \
    cd .. && rm -rf webcrawler/
WORKDIR /usr/src
RUN python -m pip install --no-cache-dir ./webcrawler*.whl
EXPOSE 6800
ENV MYSQL_DATABASE_NAME=${MYSQL_DATABASE_NAME} \
    MYSQL_DATABASE_USER=${MYSQL_DATABASE_USER} \
    MYSQL_DATABASE_PASSWORD=${MYSQL_DATABASE_PASSWORD} \
    MYSQL_DATABASE_HOST=${MYSQL_DATABASE_HOST} \
    MYSQL_DATABASE_PORT=${MYSQL_DATABASE_PORT} \
    TIKA_SERVER_HOST=${TIKA_SERVER_HOST}
CMD ["/usr/local/bin/crawl", "web"]