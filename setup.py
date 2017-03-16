#!/usr/bin/env python
import os
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


params = {
    'name': 'Webcrawler',
    'version': '1.0.0',
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
        'webcrawler': ['starturls.txt', '../LICENSE']
    },
    'entry_points': {
        'console_scripts': [
            'crawler = webcrawler.run:main',
        ],
    },
    'data_files': [
        ('/etc/', ['scrapy.cfg'])
    ],
    'install_requires': [
        'peewee==2.9.1',
        'PyMySQL==0.7.10',
        'scrapy-fake-useragent==1.0.2',
        'Scrapy==1.3.3',
        'tika==1.14',
        'python-dateutil==2.6.0',
    ]
}

setup(**params)