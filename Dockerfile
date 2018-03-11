# Containerize App
FROM python:stretch

COPY . /usr/src/webcrawler
WORKDIR /usr/src/webcrawler
RUN python -m venv --copies .env && \
    source .env/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir wheel && \
    cp dist/webcrawler*.whl ../ && deactivate && \
    cd .. && rm -rf webcrawler/
WORKDIR /usr/src
RUN python -m pip install ./webcrawler*.whl