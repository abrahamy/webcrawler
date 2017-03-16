#!/usr/bin/env python
import os
import sys
import subprocess
from setuptools import setup
from setuptools.command.install import install


class CustomInstall(install):

    def _spawn(self, cmd):
        return subprocess.run(
            cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stdout, shell=True
        )
    
    def run(self):
        super().run()

        try:
            if sys.platform is not 'linux':
                return
            
            # check if systemd is running
            out = subprocess.run(
                ['cat', '/proc/1/comm'], check=True, stdout=subprocess.PIPE
            ).stdout.decode('utf-8')
            
            if 'systemd' in out:
                self._spawn('sudo systemctl daemon-reload')
                self._spawn('sudo systemctl enable webcrawler.service')
        except Exception:
            pass


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


params = {
    'name': 'Webcrawler',
    'version': '1.0.1',
    'description': 'A web crawler bot',
    'author': 'Abraham Aondowase Yusuf',
    'author_email': 'aaondowasey@gmail.com',
    'license': read('LICENSE'),
    'url': 'https://bitbucket.org/abrahamy/webcrawler.git',
    'packages': ['webcrawler', 'webcrawler.spiders'],
    'package_dir': {
        'webcrawler': 'webcrawler',
        'webcrawler.spiders': 'webcrawler/spiders'
    },
    'package_data': {
        'webcrawler': ['starturls.txt', '../LICENSE', '../config/*.service']
    },
    'scripts': ['crawler'],
    'data_files': [
        ('/etc/', ['scrapy.cfg']),
        ('/etc/systemd/system', ['config/webcrawler.service'])
    ],
    'install_requires': [
        'peewee==2.9.1',
        'PyMySQL==0.7.10',
        'scrapy-fake-useragent==1.0.2',
        'Scrapy==1.3.3',
        'tika==1.14',
        'python-dateutil==2.6.0',
    ],
    'cmdclass': {'install': CustomInstall}
}

setup(**params)