import sys

from django.test import TestCase

from django_data_sync import models


DJANGO_DATA_SYNC_MOCK = {
}


class SyncClass(object):
    pass


class TestSyncAppModel(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.sync_app_model = models.SyncAppModel(
            app_model='test_model.SyncClass')

    def test_str(self):
        self.assertEqual(str(self.sync_app_model), 'test_model.SyncClass')

    def test_unicode(self):
        if sys.version_info < (3, ):
            self.assertEqual(unicode(self.sync_app_model), u'test_model.SyncClass')

    def test_get_elements_data(self):
        self.sync_app_model.get_elements_data_json = {'key': 'value'}
        self.assertEqual(self.sync_app_model.get_elements_data, {'key': 'value'})

        self.sync_app_model.get_elements_data = {'key2': 'value2'}
        self.assertEqual(self.sync_app_model.get_elements_data_json, {'key2': 'value2'})

    def test_load_elements_data(self):
        self.sync_app_model.load_elements_data_json = {'key': 'value'}
        self.assertEqual(self.sync_app_model.load_elements_data, {'key': 'value'})

        self.sync_app_model.load_elements_data = {'key2': 'value2'}
        self.assertEqual(self.sync_app_model.load_elements_data_json, {'key2': 'value2'})

    def test_last_sync_info(self):
        self.sync_app_model.last_sync_info_json = {'key': 'value'}
        self.assertEqual(self.sync_app_model.last_sync_info, {'key': 'value'})

        self.sync_app_model.last_sync_info = {'key2': 'value2'}
        self.assertEqual(self.sync_app_model.last_sync_info_json, {'key2': 'value2'})

    def test_get_class(self):
        self.assertEqual(self.sync_app_model.get_class('django_data_sync.tests.test_models.SyncClass'), SyncClass)

    def test_get_elements_class(self):
        self.sync_app_model.get_elements_class_path = 'django_data_sync.tests.test_models.SyncClass'
        self.assertEqual(self.sync_app_model.get_elements_class, SyncClass)

    def test_load_elements_class(self):
        self.sync_app_model.load_elements_class_path = 'django_data_sync.tests.test_models.SyncClass'
        self.assertEqual(self.sync_app_model.load_elements_class, SyncClass)

    def test_absolute_url(self):
        self.sync_app_model.pk = 1
        self.assertEqual(self.sync_app_model.get_absolute_url(),
                         u'/groups-manager/sync-app-model/1/')
