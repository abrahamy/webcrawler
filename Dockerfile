# Containerize App
FROM python:stretch

LABEL Author="Abraham Yusuf <aaondowasey@gmail.com>"\
    Client="Cubic Multi Services Limited"

COPY . /usr/src/webcrawler
WORKDIR /usr/src/webcrawler
RUN pip install --no-cache-dir wheel && \
    python setup.py bdist_wheel && \
    pip install --no-cache-dir dist/webcrawler*.whl && \
    cd .. && rm -rf webcrawler/
EXPOSE 6800
ENTRYPOINT [ "./entrypoint.sh" "web"]