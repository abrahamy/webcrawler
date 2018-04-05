#!/usr/bin/env python
#
# Copyright (C) Abraham Aondowase Yusuf - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Written by Abraham Aondowase Yusuf <aaondowasey@gmail.com>, April 2018
import os
import uuid
import shutil
from pip.req import parse_requirements as pip_parse_requirements
from distutils import log
from setuptools import find_packages, setup
from setuptools.command.install import install
from pkg_resources import Requirement, resource_filename


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def parse_requirements():
    '''Naively parse the requirements.txt file'''
    BASE_DIR = os.path.realpath(os.path.dirname(__file__))
    requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
    requirements = [str(r).split(' ')[0].strip()
                    for r in pip_parse_requirements(requirements_file, session=uuid.uuid1())]

    return requirements


class InstallCommand(install):
    '''
    Extend distutils default install command to support copying of scrapy.cfg to the
    correct /etc/scrapy.cfg
    '''

    def run(self):
        # Run base install command
        install.run(self)

        # If all went well then the package has already been installed at this point
        # move scrapy.cfg to normal location
        try:
            scrapy_config = resource_filename(
                Requirement.parse('webcrawler'), 'scrapy.cfg'
            )
            notice = 'copying {} to /etc/scrapy.cfg'.format(scrapy_config)
            self.announce(notice, level=log.INFO)

            shutil.copyfile(scrapy_config, '/etc/scrapy.cfg')
        except:
            notice = (
                'Unable to write file `/etc/scrapy.cfg`. Manually copy {} '
                'to /etc/scrapy.cfg or set the environment variable '
                '`SCRAPY_SETTINGS_MODULE=webcrawler.settings`.'
            )
            self.announce(notice, level=log.WARN)


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
            'build.sh', 'docker-compose.sample.yml', 'Dockerfile', 'entrypoint.sh',
            'LICENSE', 'README.md', 'requirements.txt', 'scrapy.cfg',
            'supervisord.conf', 'webcrawler.service',
        ],
        'api': ['requirements.txt', 'uwsgi.yml']
    },
    'entry_points': {
        'console_scripts': [
            'start_crawl = webcrawler.__main__:main'
        ]
    },
    'zip_safe': True,
    'install_requires': parse_requirements(),
    'cmdclass': {
        'install': InstallCommand
    },
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
