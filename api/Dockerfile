# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

ADD https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh /usr/bin/wait-for-it
RUN chmod +x /usr/bin/wait-for-it

COPY ./api/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt && \
    rm /requirements.txt && useradd -ms /bin/bash api

USER api
COPY ./api /home/api
COPY ./webcrawler /home/api/webcrawler

RUN chmod +x /home/api/entrypoint.sh

EXPOSE 6000
WORKDIR /home/api
ENTRYPOINT [ "./entrypoint.sh" ]