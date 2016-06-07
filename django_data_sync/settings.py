from django.conf import settings


DJANGO_DATA_SYNC_SETTINGS = getattr(settings, 'DJANGO_DATA_SYNC', {})

NOTIFICATIONS_SETTINGS = {
    'function': DJANGO_DATA_SYNC_SETTINGS.get('NOTIFICATIONS', {}).get('function'),
    'usernames': DJANGO_DATA_SYNC_SETTINGS.get('NOTIFICATIONS', {}).get('usernames', []),
    'groups_names': DJANGO_DATA_SYNC_SETTINGS.get('NOTIFICATIONS', {}).get('groups_names', []),
    'statuses': DJANGO_DATA_SYNC_SETTINGS.get('NOTIFICATIONS', {}).get('statuses', []),
}

DJANGO_DATA_SYNC = {
    'CONTROLLER_CLASS': DJANGO_DATA_SYNC_SETTINGS.get('CONTROLLER_CLASS', 'DictController'),
    'TEMPLATE_STYLE': DJANGO_DATA_SYNC_SETTINGS.get('TEMPLATE_STYLE', 'material'),
    'NOTIFICATIONS': NOTIFICATIONS_SETTINGS,
}

TEMPLATE_STYLES = ['material', 'bootstrap2']
if DJANGO_DATA_SYNC['TEMPLATE_STYLE'] not in TEMPLATE_STYLES:
    DJANGO_DATA_SYNC['TEMPLATE_STYLE'] = 'material'
if DJANGO_DATA_SYNC['TEMPLATE_STYLE'] != '':
    DJANGO_DATA_SYNC['TEMPLATE_STYLE'] = '/' + DJANGO_DATA_SYNC['TEMPLATE_STYLE']
