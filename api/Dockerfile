# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

COPY ./api /usr/src/api
RUN pip install --no-cache-dir -r /usr/src/api/requirements.txt && \
    rm -rf /usr/src/api && useradd -ms /bin/bash api
USER api
COPY ./api /home/api
COPY ./webcrawler /home/api/webcrawler
EXPOSE 6000
WORKDIR /home/api
ENTRYPOINT [ "/usr/local/bin/uwsgi", "--yaml", "uwsgi.yml" ]