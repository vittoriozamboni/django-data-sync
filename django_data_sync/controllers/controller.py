import abc
from collections import defaultdict
import datetime
import uuid


class BaseController(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Must set:
        self.queue: list of app_models to sync
        self.messages: list of controller messages
        self.app_models: collectors of app_models
        """
        self.creation_date = datetime.datetime.now()

    @abc.abstractmethod
    def setup_app_model(self, app_model, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get_app_model(self, app_model):
        raise NotImplementedError

    @abc.abstractmethod
    def get_status(self, app_model):
        raise NotImplementedError

    @abc.abstractmethod
    def set_status(self, app_model, status):
        raise NotImplementedError

    @abc.abstractmethod
    def set_resync(self, app_model, resync):
        raise NotImplementedError

    @abc.abstractmethod
    def add_message(self, app_model, message):
        raise NotImplementedError

    @abc.abstractmethod
    def set_start_date(self, app_model, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def set_completion_date(self, app_model, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_from_queue(self, app_model):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_app_model(self, app_model):
        raise NotImplementedError

    def start_sync(self, app_model, **kwargs):
        start_date = kwargs.get('start_date', None)
        self.set_status(app_model, 'running')
        self.add_message(app_model, 'Start operation')
        self.set_start_date(app_model, start_date=start_date)

    def complete_sync(self, app_model, status, **kwargs):
        message = kwargs.get('message', None)
        if message is None:
            if status == 'success':
                message = 'Completed successfully'
            elif status == 'failed':
                message = 'Operation failed'
        self.set_status(app_model, status)
        self.add_message(app_model, message)
        self.set_completion_date(app_model)
        self.remove_from_queue(app_model)


class DictController(BaseController):

    def __init__(self):
        super(DictController, self).__init__()
        self.queue = []
        self.messages = []
        self.app_models = defaultdict(dict)

    def setup_app_model(self, app_model, **kwargs):
        if self.app_models[app_model]:
            self.set_resync(app_model, True)
            self.queue.append(app_model)
            return

        submit_code = kwargs.get('submit_code', '%s' % uuid.uuid4())
        submission_date = kwargs.get('submission_date', datetime.datetime.now())
        dependencies = kwargs.get('dependencies', [])
        is_dependency = kwargs.get('is_dependency', False)
        self.app_models[app_model] = {
            'app_model': app_model,
            'status': None,
            'messages': [],
            'submit_code': submit_code,
            'dependencies': dependencies,
            'completion_date': None,
            'submission_date': submission_date,
            'start_date': submission_date,
            'resync': False,
            'is_dependency': is_dependency,
            'synced_elements': [],
        }
        self.queue.append(app_model)

    def get_app_model(self, app_model):
        return self.app_models.get(app_model)

    def get_status(self, app_model):
        return self.app_models.get(app_model, {}).get('status')

    def set_status(self, app_model, status):
        self.app_models[app_model]['status'] = status

    def set_resync(self, app_model, resync):
        self.app_models[app_model]['resync'] = resync

    def add_message(self, app_model, message):
        time_message = (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        if app_model == '':
            self.messages.append(time_message)
        else:
            self.app_models[app_model]['messages'].append(time_message)

    def set_synced_elements(self, app_model, synced_elements):
        self.app_models[app_model]['synced_elements'] = synced_elements

    def set_start_date(self, app_model, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now()
        self.app_models[app_model]['start_date'] = start_date

    def set_completion_date(self, app_model, completion_date=None):
        if completion_date is None:
            completion_date = datetime.datetime.now()
        self.app_models[app_model]['completion_date'] = completion_date

    def remove_from_queue(self, app_model):
        """This method is not semaphore-proof."""
        queue = []
        removed = False
        for queued_app_model in self.queue:
            if queued_app_model == app_model and not removed:
                removed = True
            else:
                queue.append(queued_app_model)
        self.queue = queue

    def remove_app_model(self, app_model):
        try:
            del self.app_models[app_model]
        except KeyError:
            pass


def get_controller(controller_class):
    if controller_class == 'DictController':
        sync_controller = DictController()
    else:
        raise Exception("Invalid controller class: %s" % controller_class)
    return sync_controller
