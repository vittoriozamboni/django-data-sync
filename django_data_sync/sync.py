import settings
import uuid

from controllers import controller

sync_controller = controller.get_controller(settings.DJANGO_DATA_SYNC['CONTROLLER_CLASS'])


def ordered_app_model_instances(app_model_instance):
    requires = app_model_instance.requires.all()
    print 'requires for %s: %s' % (app_model_instance, requires)
    requires_list = []
    if len(requires):
        for require in requires:
            require_list = ordered_app_model_instances(require)
            requires_list = require_list + requires_list
    return requires_list + [app_model_instance]


def setup_sync_app_model(app_model_instance, submit_code=None, is_dependency=False):
    if submit_code is None:
        submit_code = uuid.uuid4()

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


def sync_app_model(app_model_instance):
    sync_controller.start_sync(app_model_instance.app_model)
    try:
        e_get, e_load = (app_model_instance.get_elements_class(app_model_instance),
                         app_model_instance.load_elements_class(app_model_instance))
        sync_controller.add_message(app_model_instance.app_model, 'Get elements')
        elements = e_get.get_elements()
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
    sync_controller.complete_sync(app_model_instance.app_model, status, message=message)
    app_model_data = sync_controller.get_app_model(app_model_instance.app_model)

    app_model_instance.last_sync_date = app_model_data['completion_date']
    app_model_instance.save()

    if not app_model_data['is_dependency']:
        sync_controller.remove_app_model(app_model_instance.app_model)
    return app_model_data


def sync_app_models(app_model_instance):
    setup_sync_app_model(app_model_instance)
    app_model_instances = ordered_app_model_instances(app_model_instance)
    results = []
    for app_model_instance in app_model_instances:
        results.append(sync_app_model(app_model_instance))
    return results
