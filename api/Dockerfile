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
ENTRYPOINT [ "entrypoint.sh" ]