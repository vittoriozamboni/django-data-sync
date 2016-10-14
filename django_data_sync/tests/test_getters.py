import datetime
import sys

from httmock import response, urlmatch, HTTMock
from django.test import TestCase

from connection_manager.connection import RemoteConnection

from django_data_sync import models, getters


DJANGO_DATA_SYNC_MOCK = {
}


@urlmatch(netloc=r'(.*)?api\.example\.com')
def api_example_com_json_mock(url, request):
    headers = {'content-type': 'application/json'}
    if url.query == '':
        content = {'key': 'value'}
    elif 'elements=1' in url.query.split('&'):
        content = {'elements': [
            {'id': 1, 'edit_date': '20160820'},
            {'id': 2, 'edit_date': '20160824'},
        ]}
        if 'last_edit_date_from' in url.query:
            content['elements'] = content['elements'][:1]
            content['last_edit_date_from'] = [p.split('=')[1] for p in url.query.split('&')][-1]
    return response(200, content, headers, None, 1, request)


class SyncClass(object):
    pass


class TestAPIMixin(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.app_model = models.SyncAppModel(app_model='django_data_sync.tests.test_getters.SyncClass')
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
