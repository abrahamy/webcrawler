Installation (CentOS)
=====================
* Install Docker
```
$ wget -qO- https://get.docker.com/ | sh
$ usermod -aG docker $(whoami)
$ systemctl enable docker
$ systemctl start docker
```
* Install Docker Compose
```
$ yum install epel-release
$ yum install -y python-pip
$ pip install docker-compose
```
* Install pwgen
```
$ yum install pwgen
```
* Upgrade System Python
```
$ yum upgrade python*
```
* Clone the Repository
```
$ cd /opt
$ git clone git@gitlab.com:abrahamy/webcrawler.git
```
* Build Containers
```
$ cd webcrawler
$ ./build.sh
```
* Register SystemD Service
```
$ cp webcrawler.service /etc/systemd/system/webcrawler.service
$ systemctl daemon-reload
$ systemctl enable webcrawler.service
```
* Run It
```
$ systemctl start webcrawler.service
```