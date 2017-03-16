#!/usr/bin/env python

from setuptools import setup


params = {
    'name': 'Webcrawler',
    'version': '1.0.0',
    'description': 'A web crawler bot',
    'author': 'Abraham Aondowase Yusuf',
    'author_email': 'aaondowasey@gmail.com',
    'url': 'https://bitbucket.org/abrahamy/webcrawler.git',
    'packages': ['webcrawler',],
    'package_dir': {'webcrawler': 'webcrawler'},
    'package_data': {
        '': ['LICENSE',],
        'webcrawler': ['starturls.txt',]
    },
    'scripts': [
        'crawler'
    ],
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