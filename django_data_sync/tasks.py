import logging

from celery import shared_task

logging.basicConfig()
logger = logging.getLogger('Dashboard')

import models, sync


@shared_task
def auto_sync_app_models():
    for app_model in models.SyncAppModel.objects.filter(auto_sync=True):
        logger.info('Sync %s' % app_model)
        results = sync.sync_app_models(app_model)
        logger.info('%s Sync Results' % app_model)
        for synced_model in results:
            logger.info('  Synced %s: *** %s ***' %
                        (synced_model['app_model'], synced_model['status']))
            logger.info('  Messages:')
            for message in synced_model['messages']:
                logger.info('   - %s' % unicode(message[1]).encode())
            logger.info('\n')
