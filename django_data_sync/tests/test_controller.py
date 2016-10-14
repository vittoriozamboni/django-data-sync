import datetime
import sys

from httmock import response, urlmatch, HTTMock
from django.test import TestCase


from django_data_sync import models, getters
from django_data_sync.controllers import controller


class DummyController(controller.BaseController):

    def __init__(self):
        super(DummyController, self).__init__()
        self.queue = []
        self.messages = []
        self.app_models = {}

    def setup_app_model(self, app_model, **kwargs):
        self.app_models[app_model] = {
            'status': 'init',
            'messages': [],
            'start_date': None,
            'completion_date': None,
        }
        self.queue.append(app_model)

    def get_app_model(self, app_model):
        raise NotImplementedError

    def get_status(self, app_model):
        raise NotImplementedError

    def set_status(self, app_model, status):
        self.app_models[app_model]['status'] = status

    def set_resync(self, app_model, resync):
        raise NotImplementedError

    def add_message(self, app_model, message):
        self.app_models[app_model]['messages'].append(message)

    def set_start_date(self, app_model, **kwargs):
        # only for DummyController, to check with assertion
        date = kwargs['start_date']
        self.app_models[app_model]['start_date'] = date

    def set_completion_date(self, app_model, **kwargs):
        # only for DummyController, to check with assertion
        self.app_models[app_model]['completion_date'] = \
            self.app_models[app_model]['start_date']

    def remove_from_queue(self, app_model):
        self.queue.remove(app_model)

    def remove_app_model(self, app_model):
        raise NotImplementedError


class TestBaseController(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.controller = DummyController()
        self.controller.setup_app_model('SyncClass')

    def test_get_app_model(self):
        self.controller.setup_app_model('SyncClass')

    def test_start_sync(self):
        start_date = datetime.datetime.now()
        self.controller.start_sync('SyncClass', start_date=start_date)
        self.assertEqual(self.controller.app_models['SyncClass']['start_date'], start_date)
        self.assertEqual(self.controller.app_models['SyncClass']['status'], 'running')
        self.assertEqual(self.controller.app_models['SyncClass']['messages'], ['Start operation'])

    def test_complete_sync(self):
        start_date = datetime.datetime.now()
        self.controller.start_sync('SyncClass', start_date=start_date)
        self.controller.complete_sync('SyncClass', 'success')
        self.assertEqual(self.controller.app_models['SyncClass']['completion_date'], start_date)
        self.assertEqual(self.controller.app_models['SyncClass']['status'], 'success')
        self.assertEqual(self.controller.app_models['SyncClass']['messages'],
                         ['Start operation', 'Completed successfully'])
        self.assertEqual(self.controller.queue, [])

    def test_complete_sync_fail(self):
        start_date = datetime.datetime.now()
        self.controller.start_sync('SyncClass', start_date=start_date)
        self.controller.complete_sync('SyncClass', 'failed')
        self.assertEqual(self.controller.app_models['SyncClass']['status'], 'failed')
        self.assertEqual(self.controller.app_models['SyncClass']['messages'],
                         ['Start operation', 'Operation failed'])


class TestDictController(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.controller = controller.DictController()

    def test_init(self):
        self.assertEqual(self.controller.queue, [])
        self.assertEqual(self.controller.messages, [])
        self.assertEqual(self.controller.app_models['test'], {})

    def test_setup_app_model(self):
        submission_date = datetime.datetime.now()
        self.controller.setup_app_model('SyncClass', submission_date=submission_date, submit_code='sa')
        self.assertEqual(self.controller.queue, ['SyncClass'])
        self.assertEqual(
            self.controller.app_models['SyncClass'], {
                'app_model': 'SyncClass',
                'status': None,
                'messages': [],
                'submit_code': 'sa',
                'dependencies': [],
                'completion_date': None,
                'submission_date': submission_date,
                'start_date': submission_date,
                'resync': False,
                'is_dependency': False,
                'synced_elements': [],
            })

    def test_setup_app_model_resync(self):
        self.controller.setup_app_model('SyncClass')
        self.assertFalse(self.controller.app_models['SyncClass']['resync'])
        self.controller.setup_app_model('SyncClass')
        self.assertTrue(self.controller.app_models['SyncClass']['resync'])

    def test_get_app_model(self):
        self.controller.setup_app_model('SyncClass')
        self.assertEqual(self.controller.get_app_model('SyncClass'),
                         self.controller.app_models['SyncClass'])
        self.assertEqual(self.controller.get_app_model('NoClass'), None)

    def test_get_status(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.app_models['SyncClass']['status'] = 'init'
        self.assertEqual(self.controller.get_status('SyncClass'), 'init')
        self.assertEqual(self.controller.get_status('NoClass'), None)

    def test_set_status(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.set_status('SyncClass', 'init')
        self.assertEqual(self.controller.get_status('SyncClass'), 'init')

    def test_set_resync(self):
        self.controller.setup_app_model('SyncClass')
        self.assertFalse(self.controller.app_models['SyncClass']['resync'])
        self.controller.set_resync('SyncClass', True)
        self.assertTrue(self.controller.app_models['SyncClass']['resync'])

    def test_add_message(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.add_message('SyncClass', 'test message')
        self.assertEqual(self.controller.app_models['SyncClass']['messages'][0][1], 'test message')
        self.controller.add_message('', 'test message class')
        self.assertEqual(self.controller.messages[0][1], 'test message class')

    def test_set_synced_elements(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.set_synced_elements('SyncClass', [{'id': 1}, {'id': 2}])
        self.assertEqual(self.controller.app_models['SyncClass']['synced_elements'],
                         [{'id': 1}, {'id': 2}])

    def test_set_start_date(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.set_start_date('SyncClass')
        self.assertNotEqual(self.controller.app_models['SyncClass']['start_date'], None)
        self.assertNotEqual(self.controller.app_models['SyncClass']['start_date'],
                            self.controller.app_models['SyncClass']['submission_date'])
        start_date = datetime.datetime.now()
        self.controller.set_start_date('SyncClass', start_date)
        self.assertEqual(self.controller.app_models['SyncClass']['start_date'], start_date)

    def test_set_completion_date(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.set_completion_date('SyncClass')
        self.assertNotEqual(self.controller.app_models['SyncClass']['completion_date'], None)
        completion_date = datetime.datetime.now()
        self.controller.set_completion_date('SyncClass', completion_date)
        self.assertEqual(self.controller.app_models['SyncClass']['completion_date'], completion_date)

    def test_remove_from_queue(self):
        self.controller.setup_app_model('SyncClass')
        self.controller.setup_app_model('NoClass')
        self.controller.setup_app_model('SyncClass')
        self.assertEqual(self.controller.queue, ['SyncClass', 'NoClass', 'SyncClass'])
        self.controller.remove_from_queue('SyncClass')
        self.assertEqual(self.controller.queue, ['NoClass', 'SyncClass'])
        self.controller.remove_from_queue('SyncClass')
        self.assertEqual(self.controller.queue, ['NoClass'])
        self.controller.remove_from_queue('SyncClass')
        self.assertEqual(self.controller.queue, ['NoClass'])
        self.controller.remove_from_queue('NoClass')
        self.assertEqual(self.controller.queue, [])

    def test_remove_app_model(self):
        self.controller.setup_app_model('SyncClass')
        self.assertIsNotNone(self.controller.get_app_model('SyncClass'))
        self.controller.remove_app_model('SyncClass')
        self.assertIsNone(self.controller.get_app_model('SyncClass'))
        self.controller.remove_app_model('NoClass')


class TestFunctions(TestCase):

    def test_get_controller(self):
        dict_controller = controller.get_controller('DictController')
        self.assertIsInstance(dict_controller, controller.DictController)
        with self.assertRaises(Exception):
            controller.get_controller('test')
