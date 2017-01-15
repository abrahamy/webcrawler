Installation
============

* Install [docker](https://docs.docker.com/engine/installation/linux/ubuntulinux/ "Install Docker on Ubuntu - Docker")
* Pull [tika server](https://store.docker.com/community/images/logicalspark/docker-tikaserver "Docker Store") image from Docker Store
`$ docker pull logicalspark/docker-tikaserver`
* Pull [postgres](https://store.docker.com/images/022689bf-dfd8-408f-9e1c-19acac32e57b?tab=description "postgres - Docker Store") image from Docker Store
`$ docker pull postgres`
* Pull [pgadmin4](https://store.docker.com/community/images/fenglc/pgadmin4 "Docker Store") image from Docker Store
`$ docker pull fenglc/pgadmin4`
* Get project source code
```
$ mkdir -p /usr/src /var/log/cmsl
$ cd /usr/src
$ rm -rf webcrawler
$ git clone https://abrahamy@bitbucket.org/abrahamy/webcrawler.git
```
* Install dependencies
```
$ deps="python python-dev libpq5 libffi-dev libpq-dev libxml2-dev build-essential"
$ apt-get update
$ apt-get install -y --no-install-recommends $deps
$ wget https://bootstrap.pypa.io/get-pip.py
$ python get-pip.py && rm get-pip.py
$ cd webcrawler
$ pip install --no-cache-dir --upgrade \
    --force-reinstall -r requirements.txt
```
* Create and run Tika container
```
$ docker run --name cmsl-tika-server -d -p 9998:9998 \
    logicalspark/docker-tikaserver
```
* Create and run PostgreSQL container
```
$ dbcontainer="cmsl-database"
$ dbuser="webcrawler"
$ dbpass=$(tr -c -d '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()' </dev/urandom | dd bs=32 count=1 2>/dev/null)
$ mkdir -p /var/lib/postgresql/data
$ docker run --name $dbcontainer \
    -e POSTGRES_USER=$dbuser POSTGRES_PASSWORD=$dbpass PGDATA=/var/lib/postgresql/data
    -v /var/lib/postgresql/data:/var/lib/postgresql/data
    -p 5432:5432
    -d postgres
```
* Initialize hstore extension on the database
```
$ docker run --rm --link $dbcontainer:postgres \
    -e PGUSER=$dbuser PGPASSWORD=$dbpass PGHOST=postgres \
    postgres psql -c "CREATE EXTENSION IF NOT EXIST hstore;"
```
* Setup pgadmin container (if required)
```
$ docker run --name cmsl-pgadmin \
    --link $db:postgres \
    -p 5050:5050 \
    -d fenglc/pgadmin4
```
* Run REST server
```
$ uwsgi uwsgi.yml
```
* Run web crawler
```
$ scrapy crawl cmsl
```