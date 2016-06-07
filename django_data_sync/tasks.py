from celery import shared_task

import sync


@shared_task
def auto_sync_app_models_task():
    sync.auto_sync_app_models()