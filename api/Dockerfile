# Containerize Api
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

# Build a Python egg of the webcrawler
COPY . /usr/src/webcrawler
WORKDIR /usr/src/webcrawler
RUN python setup.py bdist_egg && \
    cp dist/webcrawler*.egg ../ && rm -rf ../webcrawler

# Configure and run API server
ADD ./api/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./api/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt && \
    rm /requirements.txt && useradd -ms /bin/bash api && \
    chown api:api /usr/src/webcrawler*.egg

USER api
COPY ./api /home/api
COPY ./webcrawler /home/api/webcrawler

EXPOSE  6000
WORKDIR /home/api
ENTRYPOINT [ "/entrypoint.sh" ]