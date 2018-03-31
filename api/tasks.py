import os
import logging
import requests
from celery import Celery


logger = logging.getLogger(__name__)

redis_uri = 'redis://redis:6379/0'
celery = Celery('api', broker=redis_uri, backend=redis_uri)


class InvalidEnvironmentException(Exception):
    pass


def get_egg_filename():
    '''Gets the webcrawler .egg file'''
    eggversion = os.getenv('EGG_VERSION')
    if not eggversion:
        logger.error(
            'InvalidEnvironmentException: `EGG_VERSION` environment variable is not set!')
        raise InvalidEnvironmentException(
            '`EGG_VERSION` environment variable is not set!')

    return '/webcrawler-{eggversion}-py3.6.egg'.format(eggversion=eggversion)


SCRAPY_PROJECT = 'webcrawler'
SCRAPY_DAEMON_URL = 'http://{}:6800'.format(os.getenv('SCRAPYD_HOST'))


@celery.task(name='register', serializer='json')
def register_project():
    '''
    Register the webcrawler project with the scrapyd server
    '''
    version = 'r{}'.format(os.getenv('EGG_VERSION', '2.0.0').replace('.', ''))
    data = {
        'project': SCRAPY_PROJECT,
        'version': version
    }
    files = {'file': open(get_egg_filename(), 'rb')}
    url = '{}/addversion.json'.format(SCRAPY_DAEMON_URL)

    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        logger.error(
            'Celery task `register_project` has failed! Reason: {}'.format(str(e)))
        raise e


@celery.task(name='restart', serializer='json')
def restart_spider(jobid):
    '''
    Stop the currently running news spider and schedule a new run

    Arguments:
        jobid: job id of currently running news spider instance
    '''
    if cancel_job(jobid):
        schedule_job(jobid)


def cancel_job(jobid):
    '''Cancel the currently running spider with the given job id'''
    cancel_url = '{}/cancel.json'.format(SCRAPY_DAEMON_URL)
    data = {
        'project': SCRAPY_PROJECT,
        'job': jobid
    }

    try:
        requests.post(cancel_url, data=data)
        return True
    except Exception as _:
        return False


def schedule_job(jobid):
    # @todo: implement
    pass
