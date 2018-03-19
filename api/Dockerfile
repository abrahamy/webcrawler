# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

COPY ./api /usr/src/api
COPY ./webcrawler /usr/src/api/webcrawler
WORKDIR /usr/src/api
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 80
ENTRYPOINT [ "/usr/local/bin/uwsgi", "--http", "0.0.0.0:80", "--uid", "uwsgi", \
    "--plugins", "python3", "--protocol", "uwsgi", \
    "--logto", "logs/uWSGI.log", \
    "--wsgi", "server:__hug_wsgi__" ]