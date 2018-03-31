from celery import Celery


celery = Celery(__name__, broker='redis://redis:6379/0')


@celery.task
def register_project():
    '''
    Register the webcrawler project with the scrapyd server
    '''
    print('registering project...')  # @todo: implement


@celery.task
def restart_spider(config):
    '''
    Stop the currently running news spider and schedule a new run

    Arguments:
        config: the news spider configuration
    '''
    print('restarting spider...')  # @todo: implement
