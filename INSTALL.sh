# Installation Script (see README.md)

# define variables
ubuntu_version=trusty
docker_version=1.12.6-0~ubuntu-trusty
docker_compose_version=1.10.0-rc2
python_version=python3.4
build_deps=" \
    $python_version $python_version-dev $python_version-venv \
    libpq5 libffi-dev libpq-dev libxml2-dev \
    libxslt-dev build-essential \
"

# install docker
apt-get update
apt-get install apt-transport-https ca-certificates
apt-key adv \
    --keyserver hkp://ha.pool.sks-keyservers.net:80 \
    --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-$ubuntu_version main" | sudo tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual
apt-get install docker-engine=$docker_version

# install docker-compose
apt-get install curl
curl -L https://github.com/docker/compose/releases/download/$docker_compose_version/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# pull tika server docker image
docker pull logicalspark/docker-tikaserver

# pull PostgreSQL docker image
docker pull postgres

# pull pgadmin4 docker image
docker pull fenglc/pgadmin4

# get project source code
mkdir -p /usr/src /var/log/cmsl
cd /usr/src
rm -rf webcrawler
echo "preparing to clone repository. At prompt enter bitbucket password."
git clone https://abrahamy@bitbucket.org/abrahamy/webcrawler.git

# install system dependencies
apt-get install -y --no-install-recommends $build_deps
wget https://bootstrap.pypa.io/get-pip.py
$python_version get-pip.py && rm get-pip.py

# create/activate virtual environment and install project requirements
cd /usr/src/webcrawler
$python_version -m venv --copies venv && source venv/bin/activate
pip install --no-cache-dir --upgrade \
    --force-reinstall -r requirements.txt

# create and run PostgreSQL and Tika containers
docker-compose -f /usr/src/webcrawler/docker-compose.yml \
    --project-name=cmsl up -d

# initialize hstore extension on the database
docker run --rm --link cmsl-database:db --net cmsl_webcrawler \
    -e PGUSER=webcrawler PGPASSWORD=atVLkE7AW2OkaAxr PGHOST=db \
    postgres psql -c "CREATE EXTENSION IF NOT EXIST hstore;"

# run REST server
cd /usr/src/webcrawler && source venv/bin/activate
uwsgi uwsgi.yml

# run web crawler
cd /usr/src/webcrawler && source venv/bin/activate
nohup scrapy crawl cmsl > /dev/null 2>&1 &

# install upstart system service
cp /usr/src/webcrawler/services/upstart.conf /etc/init/cmsl.conf

# install systemd system service
# cp /usr/src/webcrawler/services/systemd.service /etc/systemd/system/cmsl.service
# systemctl enable cmsl.service

# finished
echo "success!"