import os
from celery import Celery


rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER', 'webcrawler')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS', '')
broker_uri = 'pyamqp://{user}:{password}@rabbitmq//'.format(
    user=rabbitmq_user, password=rabbitmq_password)


celery = Celery(__name__, broker=broker_uri)


@celery.task
def register_project():
    '''
    Register the webcrawler project with the scrapyd server
    '''
    pass  # @todo: implement


@celery.task
def restart_spider(config):
    '''
    Stop the currently running news spider and schedule a new run

    Arguments:
        config: the news spider configuration
    '''
    pass  # @todo: implement
