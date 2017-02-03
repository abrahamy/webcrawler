Installation
============

* Install system dependencies
```
$ apt update
$ apt install -y apt-transport-https ca-certificates python3 \
    python3-dev python3-venv build-essential libpq5 libffi-dev \
    libpq-dev libxml2-dev libxslt-dev libssl-dev curl
```
* Download and configure Tika server
```
$ TIKA_VERSION=1.14
$ TIKA_SERVER_URL=https://www.apache.org/dist/tika/tika-server-$TIKA_VERSION.jar
$ apt install -y openjdk-8-jre-headless gdal-bin tesseract-ocr \
    tesseract-ocr-eng tesseract-ocr-ita tesseract-ocr-fra \
    tesseract-ocr-spa tesseract-ocr-deu
$ mkdir -p /opt/tikaserver
$ curl -sSL https://people.apache.org/keys/group/tika.asc | gpg --import -
$ curl -sSL "$TIKA_SERVER_URL.asc" -o /opt/tikaserver/tika-server-${TIKA_VERSION}.jar.asc
$ curl -sSL "$TIKA_SERVER_URL" -o /opt/tikaserver/tika-server-${TIKA_VERSION}.jar
```
* Install PostgreSQL database
```
$ UBUNTU_VERSION=xenial # or trusty or precise
$ echo "deb http://apt.postgresql.org/pub/repos/apt/ $UBUNTU_VERSION-pgdg main" \
    | tee /etc/apt/sources.list.d/pgdg.list
$ curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
$ apt update && apt install -y postgresql postgresql-contrib
```
* Initialize the webcrawler database
```
$ DB_PASSWORD=$(tr -c -d '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' </dev/urandom | dd bs=32 count=1 2>/dev/null;)
$ DB_SCRIPT=" \
        CREATE DATABASE IF NOT EXIST webcrawler; \
        CREATE EXTENSION IF NOT EXIST hstore; \
        ALTER ROLE postgres WITH ENCRYPTED PASSWORD "$DB_PASSWORD"; \
    "
$ sudo -u postgres psql -c $DB_SCRIPT
```
* Download the source code from bitbucket and install Python dependencies
```
$ cd /opt && git clone https://abrahamy@bitbucket.org/abrahamy/webcrawler.git
$ cd webcrawler
$ curl -sSL https://bootstrap.pypa.io/get-pip.py | python3 -
$ python3 -m venv --copies venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
* Install and configure supervisor to run the services at bootup
```
$ apt install -y supervisor
$ cp /opt/webcrawler/config/supervisor.conf /etc/supervisor/conf.d/cmsl.conf
```
* Restart server and verify that Tika server, REST api and crawler are started
```
$ reboot
----
$ curl -X GET http://localhost:9998 # check tikaserver
$ curl -X GET http://localhost/ # check REST api
```