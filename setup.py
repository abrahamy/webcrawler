#!/usr/bin/env python
import os
import uuid
from pip.req import parse_requirements as pip_parse_requirements
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def parse_requirements():
    '''Naively parse the requirements.txt file'''
    BASE_DIR = os.path.realpath(os.path.dirname(__file__))
    requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
    requirements = [str(r).split(' ')[0].strip()
                    for r in pip_parse_requirements(requirements_file, session=uuid.uuid1())]

    return requirements


params = {
    'name': 'webcrawler',
    'version': '2.0.0',
    'description': 'A web crawler bot',
    'author': 'Abraham Aondowase Yusuf',
    'author_email': 'aaondowasey@gmail.com',
    'license': read('LICENSE'),
    'url': 'https://bitbucket.org/abrahamy/webcrawler.git',
    'packages': find_packages(exclude=["tests/*"]),
    'package_dir': {
        'api': 'api',
        'webcrawler': 'webcrawler',
        'webcrawler.spiders': 'webcrawler/spiders'
    },
    'package_data': {
        '': [
            '.env.sample', 'build.sh', 'docker-compose.sample.yml',
            'LICENSE', 'README.md', 'requirements.txt', 'scrapy.cfg',
            'scrapyd_Dockerfile',
        ],
        'api': ['Dockerfile', 'entrypoint.sh', 'requirements.txt', 'uwsgi.yml'],
        'webcrawler': ['starturls.txt', ]
    },
    'data_files': [('/etc/', ['scrapy.cfg']), ],
    'entry_points': {
        'console_scripts': [
            'start_crawl = webcrawler.__main__:main'
        ]
    },
    'zip_safe': True,
    'install_requires': parse_requirements(),
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'License :: Other/Proprietary License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
}

setup(**params)
