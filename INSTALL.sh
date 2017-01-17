# Installation Script (see README.md)

# define variables
export POSTGRES_USER=webcrawler
export POSTGRES_PASSWORD=$(tr -c -d '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' </dev/urandom | dd bs=32 count=1 2>/dev/null;)

ubuntu_version=trusty
docker_version=1.12.6-0~ubuntu-trusty
docker_compose_version=1.10.0-rc2
python_version=python3.4
project_root=/usr/src
settings_module="$project_root/webcrawler/webcrawler/settings.py"
pg_data=/var/lib/postgres/data
log_path=/var/log/cmsl
build_deps=" \
    $python_version $python_version-dev $python_version-venv \
    libpq5 libffi-dev libpq-dev libxml2-dev \
    libxslt-dev build-essential \
"
sql_query="\
-- enable hstore extension on the database \
CREATE EXTENSION IF NOT EXISTS hstore; \
-- create a user with read-only access to the database \
CREATE ROLE cmsl WITH LOGIN ENCRYPTED PASSWORD 'cmslpass'; \
GRANT CONNECT ON DATABASE $POSTGRES_USER TO cmsl; \
GRANT USAGE ON SCHEMA public TO cmsl; \
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cmsl; \
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO cmsl; \
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO cmsl; \
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO cmsl; \
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
curl -L \
    https://github.com/docker/compose/releases/download/$docker_compose_version/docker-compose-`uname -s`-`uname -m` \
    > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# pull tika server docker image
docker pull logicalspark/docker-tikaserver

# pull PostgreSQL docker image
docker pull postgres

# pull pgadmin4 docker image
docker pull fenglc/pgadmin4

# get project source code
mkdir -p $project_root $log_path $pg_data
cd $project_root
rm -rf webcrawler
echo "preparing to clone repository. At prompt enter bitbucket password."
git clone https://abrahamy@bitbucket.org/abrahamy/webcrawler.git

# replace password in settings file with the random generated one
sed -ie "s/super-secret-password/$POSTGRES_PASSWORD/g" $settings_module

# install system dependencies
apt-get install -y --no-install-recommends $build_deps
wget https://bootstrap.pypa.io/get-pip.py
$python_version get-pip.py && rm get-pip.py

# create/activate virtual environment and install project requirements
cd $project_root/webcrawler
$python_version -m venv --copies venv && source venv/bin/activate
$python_version -m pip install --upgrade --force-reinstall \
    -r requirements.txt

# create and run PostgreSQL and Tika containers
docker-compose -f $project_root/webcrawler/docker-compose.yml \
    --project-name=cmsl up -d

# initialize hstore extension on the database
docker run --rm --link cmsl-database:db --net cmsl_webcrawler \
    -e PGUSER=$POSTGRES_USER \
    -e PGPASSWORD=$POSTGRES_PASSWORD \
    -e PGHOST=db postgres psql -c $sql_query

# run REST server
uwsgi uwsgi.yml

# run web crawler
nohup scrapy crawl cmsl > /dev/null 2>&1 &

# install upstart system service
cp $project_root/webcrawler/services/upstart.conf /etc/init/cmsl.conf

# install systemd system service
# cp $project_root/webcrawler/services/systemd.service /etc/systemd/system/cmsl.service
# systemctl enable cmsl.service

# finished
echo "success!"