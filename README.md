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
* Install system dependencies
```
$ deps="python3.4 python3.4-dev python3.4-venv libpq5 \
    libffi-dev libpq-dev libxml2-dev libxslt-dev build-essential"
$ apt-get update
$ apt-get install -y --no-install-recommends $deps
$ wget https://bootstrap.pypa.io/get-pip.py
$ python3.4 get-pip.py && rm get-pip.py
```
* Create/activate virtual environment and install project requirements
```
$ cd /usr/src/webcrawler
$ python3.4 -m venv --copies venv && source venv/bin/activate
$ pip install --no-cache-dir --upgrade \
    --force-reinstall -r requirements.txt
```
* Create and run PostgreSQL and Tika containers
```
$ cd /usr/src/webcrawler
$ docker-compose --project-name=cmsl up -d
```
* Initialize hstore extension on the database
```
$ docker run --rm --link cmsl-database:db --net cmsl_webcrawler \
    -e PGUSER=webcrawler PGPASSWORD=atVLkE7AW2OkaAxr PGHOST=db \
    postgres psql -c "CREATE EXTENSION IF NOT EXIST hstore;"
```
* Run REST server
```
$ cd /usr/src/webcrawler && source venv/bin/activate
$ uwsgi uwsgi.yml
```
* Run web crawler
```
$ cd /usr/src/webcrawler && source venv/bin/activate
$ scrapy crawl cmsl
```