# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

RUN useradd -ms /bin/bash api
USER api
COPY ./api /home/api
COPY ./webcrawler /home/api/webcrawler
WORKDIR /home/api
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
ENTRYPOINT [ "/usr/local/bin/uwsgi", "--http", "0.0.0.0:80", "--uid", "api", \
    "--plugins", "python3", "--protocol", "uwsgi", \
    "--logto", "logs/uWSGI.log", \
    "--wsgi", "server:__hug_wsgi__" ]