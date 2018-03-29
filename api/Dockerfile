# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

ADD ./api/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./api/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt && \
    rm /requirements.txt && useradd -ms /bin/bash api

USER api
COPY ./api /home/api
COPY ./webcrawler /home/api/webcrawler

EXPOSE 6000
WORKDIR /home/api
ENTRYPOINT [ "/entrypoint.sh" ]