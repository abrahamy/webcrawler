Installation
============
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
* Upgrade System Python
```
$ yum upgrade python*
```
* Clone the Repository
```
$ git clone git@gitlab.com:abrahamy/webcrawler.git
```
* Build Containers
```
$ cd webcrawler
$ ./build.sh
```
* Run It
```
$ docker-compose up
```