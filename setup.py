#!/usr/bin/env python
import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class CustomInstall(install):
    def _spawn(self, cmd):
        return subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stdout,
            shell=True)

    def enable_and_start_systemd_service(self, service):
        self._spawn('systemctl daemon-reload')
        self._spawn('systemctl enable {}.service'.format(service))
        self._spawn('systemctl start {}.service'.format(service))

    def run(self):
        super().run()

        try:
            if sys.platform is not 'linux':
                return

            # check if systemd is running
            out = subprocess.run(
                ['cat', '/proc/1/comm'], check=True,
                stdout=subprocess.PIPE).stdout.decode('utf-8')

            if 'systemd' in out:
                for service in ['webcrawler', 'newscrawler']:
                    self.enable_and_start_systemd_service(service)
        except Exception:
            pass


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


params = {
    'name':
    'webcrawler',
    'version':
    '1.1.0',
    'description':
    'A web crawler bot',
    'author':
    'Abraham Aondowase Yusuf',
    'author_email':
    'aaondowasey@gmail.com',
    'license':
    read('LICENSE'),
    'url':
    'https://bitbucket.org/abrahamy/webcrawler.git',
    'packages':
    find_packages(exclude=["features/*"]),
    'package_dir': {
        'api': 'api',
        'webcrawler': 'webcrawler',
        'webcrawler.spiders': 'webcrawler/spiders'
    },
    'package_data': {
        'api': ['Dockerfile', 'entrypoint.sh', 'requirements.txt'],
        'webcrawler': ['starturls.txt', '../LICENSE', '../config/*.service']
    },
    'scripts': ['crawl'],
    'data_files':
    [('/etc/', ['scrapy.cfg']),
     ('/etc/systemd/system',
      ['config/webcrawler.service', 'config/newscrawler.service'])],
    'install_requires': [
        'peewee==3.1.2',
        'PyMySQL==0.8.0',
        'scrapy-fake-useragent==1.1.0',
        'Scrapy==1.5.0',
        'tika==1.16',
        'python-dateutil==2.6.1',
    ],
    'cmdclass': {
        'install': CustomInstall
    }
}

setup(**params)
