import importlib

from django.conf import settings as django_settings
from django.template import loader, Context
from django.contrib.auth import get_user_model, models as auth_models


import settings


TS = settings.DJANGO_DATA_SYNC['TEMPLATE_STYLE']


def sync_get_recipients():
    to = []
    if settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['usernames']:
        to += list(get_user_model().objects.filter(
            username__in=settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['usernames']))
    if settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['groups_names']:
        groups = auth_models.Group.objects.filter(
            name__in=settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['groups_names'])
        for group in groups:
            to += list(group.user_set.all())
    return list(set(to))


def send_notification(*args, **kwargs):
    module_name, function_name = \
        settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['function'].rsplit('.', 1)
    send_function = getattr(importlib.import_module(module_name), function_name)
    return send_function(*args, **kwargs)


def sync_auto_sync_app_models(sync_operations):

    notify_statuses = list(set([s[1]['status'] for s in sync_operations]))
    if not settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['statuses']:
        return
    notification_statuses = settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['statuses']
    if not (('failed' in notification_statuses and 'failed' in notify_statuses) or \
            ('success' in notification_statuses and 'success' in notify_statuses)):
        return

    notify_users = sync_get_recipients()

    html_backbone = \
        loader.get_template('django_data_sync%s/notifications/sync_auto_sync_app_models.html' % TS)
    context = {
        'SITE_PREFIX': django_settings.BASE_URL,
        'sync_operations': sync_operations,
    }
    backbone_context = Context(context)
    html_message = html_backbone.render(backbone_context)

    return send_notification(notify_users, 'Auto Sync result', html_message)
