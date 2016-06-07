import logging
import uuid

from controllers import controller
import settings, models, notifications


logging.basicConfig()
logger = logging.getLogger('Dashboard')


sync_controller = controller.get_controller(settings.DJANGO_DATA_SYNC['CONTROLLER_CLASS'])


def ordered_app_model_instances(app_model_instance):
    requires = app_model_instance.requires.all()
    requires_list = []
    if len(requires):
        for require in requires:
            require_list = ordered_app_model_instances(require)
            requires_list = require_list + requires_list
    return requires_list + [app_model_instance]


def setup_sync_app_model(app_model_instance, submit_code=None, is_dependency=False):
    if submit_code is None:
        submit_code = '%s' % uuid.uuid4()

    requires = app_model_instance.requires.all()
    dependencies = []
    if len(requires):
        for require in requires:
            setup_sync_app_model(require, submit_code, True)
            dependencies.append(require.app_model)

    sync_controller.setup_app_model(app_model_instance.app_model,
                                    submit_code=submit_code, dependencies=dependencies,
                                    is_dependency=is_dependency)

    return sync_controller


def sync_app_model(app_model_instance, **kwargs):
    ignore_last_sync_date = kwargs.get('ignore_last_sync_date', False)
    dependency_failed = kwargs.get('dependency_failed', False)

    sync_controller.start_sync(app_model_instance.app_model)
    if not dependency_failed:
        try:
            e_get, e_load = (app_model_instance.get_elements_class(app_model_instance),
                             app_model_instance.load_elements_class(app_model_instance))
            sync_controller.add_message(app_model_instance.app_model, 'Get elements')
            elements = e_get.get_elements(auto_date=(not ignore_last_sync_date))
            sync_controller.add_message(app_model_instance.app_model,
                                        'Connected to %s' % e_get.request_result.request.url)
            sync_controller.add_message(app_model_instance.app_model,
                                        'Obtained %s elements' % len(elements))
            sync_controller.add_message(app_model_instance.app_model, 'Load elements')
            synced_elements = e_load.load_elements(elements)
            sync_controller.set_synced_elements(app_model_instance.app_model, synced_elements)
            status = 'success'
            message = None
        except Exception as e:
            status = 'failed'
            message = 'Error during sync: %s' % str(e)
    else:
        status = 'failed'
        message = 'Dependency failed'
    sync_controller.complete_sync(app_model_instance.app_model, status, message=message)
    app_model_data = sync_controller.get_app_model(app_model_instance.app_model)

    app_model_instance.last_sync_date = app_model_data['completion_date']
    app_model_instance.last_sync_status = status
    last_sync_info = {k: v for k, v in app_model_data.iteritems()}
    last_sync_info['submission_date'] = \
        last_sync_info['submission_date'].strftime("%Y-%m-%d %H:%M:%S")
    last_sync_info['completion_date'] = \
        last_sync_info['completion_date'].strftime("%Y-%m-%d %H:%M:%S")
    last_sync_info['start_date'] = \
        last_sync_info['start_date'].strftime("%Y-%m-%d %H:%M:%S")
    last_sync_info['submit_code'] = '%s' % last_sync_info['submit_code']
    app_model_instance.last_sync_info = last_sync_info
    app_model_instance.save()

    app_model_data['status'] = status

    if not app_model_data['is_dependency']:
        sync_controller.remove_app_model(app_model_instance.app_model)
    return app_model_data


def sync_app_models(app_model_instance, **kwargs):
    ignore_last_sync_date = kwargs.get('ignore_last_sync_date', False)
    setup_sync_app_model(app_model_instance)
    app_model_instances = ordered_app_model_instances(app_model_instance)
    results = []
    one_failed = False
    for app_model_instance in app_model_instances:
        sync_result = sync_app_model(app_model_instance,
                                     ignore_last_sync_date=ignore_last_sync_date,
                                     dependency_failed=one_failed)
        results.append(sync_result)
        if sync_result['status'] == 'failed':
            one_failed = True
    return {'success': not one_failed, 'results': results}


def get_sync_controller():
    return sync_controller


def auto_sync_app_models():
    sync_operations = []
    for app_model in models.SyncAppModel.objects.filter(auto_sync=True, last_sync_status='success'):
        logger.info('Sync %s' % app_model)
        sync_result = sync_app_models(app_model)
        logger.info('%s Sync Results === %s ===' % (app_model, sync_result['success']))
        for synced_model in sync_result['results']:
            logger.info('  Synced %s: *** %s ***' %
                        (synced_model['app_model'], synced_model['status']))
            logger.info('  Messages:')
            for message in synced_model['messages']:
                logger.info('   - %s' % unicode(message[1]).encode())
            logger.info('\n')
        sync_operations.append([app_model, sync_result])

    if settings.DJANGO_DATA_SYNC['NOTIFICATIONS']['function']:
        notifications.sync_auto_sync_app_models(sync_operations)
