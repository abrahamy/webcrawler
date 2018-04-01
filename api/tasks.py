import os
import json
import logging
import requests
from celery import Celery


logger = logging.getLogger(__name__)

redis_uri = 'redis://redis:6379/0'
celery = Celery('api', broker=redis_uri, backend=redis_uri)


SCRAPY_PROJECT = 'webcrawler'
SCRAPY_DAEMON_URL = 'http://{}:6800'.format(os.getenv('SCRAPYD_HOST'))
SCRAPY_SPIDERS = ('webspider', 'newsspider')


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


def schedule_job(spider, jobid=None):
    '''Schedule a spider run (also known as a job), returning the job id'''
    schedule_url = '{}/schedule.json'.format(SCRAPY_DAEMON_URL)
    data = {
        'project': SCRAPY_PROJECT,
        'spider': spider
    }
    if jobid:
        data['jobid'] = jobid

    try:
        response = requests.post(schedule_url, data=data)
        result = json.loads(response.json())

        if result['status'] is 'ok':
            return result['jobid']

    except (requests.ConnectionError, ValueError) as _:
        error = 'The scrapyd service returned an invalid JSON response!' if isinstance(
            _, ValueError) else 'Connection to scrapyd server failed!'
        logger.warning(error)

    return None


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

    except requests.ConnectionError as _:
        return False


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
    files = {'egg': open(get_egg_filename(), 'rb')}
    url = '{}/addversion.json'.format(SCRAPY_DAEMON_URL)

    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == requests.codes.ok:
            for spider in SCRAPY_SPIDERS:
                schedule_job(spider)

    except requests.ConnectionError as _:
        logger.error(
            'Celery task `register_project` has failed! Reason: Connection Error.')
        raise


@celery.task(name='restart', serializer='json')
def restart_spider(jobid):
    '''
    Stop the currently running news spider and schedule a new run

    Arguments:
        jobid: job id of currently running news spider instance
    '''
    if cancel_job(jobid):
        schedule_job(SCRAPY_SPIDERS[1], jobid=jobid)
