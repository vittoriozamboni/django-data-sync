import datetime
import sys

from httmock import response, urlmatch, HTTMock
from django.test import TestCase


from django_data_sync import models, getters, loaders
from django_data_sync.controllers import controller


@urlmatch(netloc=r'(.*)?api\.example\.com')
def api_example_com_json_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {'elements': []}
    if 'app_model=main' in url.query.split('&'):
        content = {'elements': [
            {'id': 1, 'name': 'main_1', 'edit_date': '20160820'},
            {'id': 2, 'name': 'main_2', 'edit_date': '20160824'},
        ]}
    elif 'app_model=dependency' in url.query.split('&'):
        content = {'elements': [
            {'id': 1, 'name': 'dep_1', 'edit_date': '20160820'},
            {'id': 2, 'name': 'dep_2', 'edit_date': '20160824'},
        ]}
    if 'last_edit_date_from' in url.query and len(content['elements']) > 1:
        content['elements'] = content['elements'][:1]
        content['last_edit_date_from'] = [p.split('=')[1] for p in url.query.split('&')][-1]
    return response(200, content, headers, None, 1, request)


class TestAPIMixin(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.app_model = models.SyncAppModel(
            app_model='django_data_sync.tests.test_sync.SyncClass')
        self.api_mixin = getters.APIMixin(self.app_model)

    def test_set_connection(self):
        self.api_mixin.set_connection()
        self.assertIsInstance(self.api_mixin.connection, RemoteConnection)
        # coverage test, should use cached
        self.api_mixin.set_connection()

    def test_connection(self):
        self.app_model.get_elements_data = {'connection_info': {'key': 'value'}}
        conn = self.api_mixin.connection
        self.assertEqual(conn._connection_data, {'key': 'value'})
        self.assertIsInstance(conn, RemoteConnection)

    def test_request_results(self):
        self.assertEqual(self.api_mixin.request_result, self.api_mixin._request_result)


class TestAPIJson(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.app_model = models.SyncAppModel()
        self.app_model.app_model = 'django_data_sync.tests.test_getters.SyncClass'
        self.app_model.get_elements_data = {
            'data_url': 'http://api.example.com'
        }
        self.last_sync_date = datetime.datetime.now()
        self.api_json = getters.APIJson(self.app_model)

    def test_get_elements(self):
        with HTTMock(api_example_com_json_mock):
            elements = self.api_json.get_elements()
            self.assertEqual(elements, {'key': 'value'})

    def test_get_elements_query(self):
        self.app_model.get_elements_data['data_url'] = 'http://api.example.com?elements=1'
        with HTTMock(api_example_com_json_mock):
            resp = self.api_json.get_elements()
            self.assertEqual({e['id'] for e in resp['elements']}, {1, 2})

    def test_get_elements_query_last_edit_date(self):
        self.app_model.last_sync_date = self.last_sync_date
        self.app_model.get_elements_data['data_url'] = 'http://api.example.com?elements=1'
        with HTTMock(api_example_com_json_mock):
            resp = self.api_json.get_elements()
            self.assertEqual({e['id'] for e in resp['elements']}, {1, })
            self.assertEqual(resp['last_edit_date_from'].replace('%3A', ':'),
                             self.last_sync_date.strftime('%Y-%m-%dT%H:%M:%S.%f'))


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
