from collections import OrderedDict

from django.db import models
from django.core.urlresolvers import reverse

from jsonfield import JSONField


class SyncAppModel(models.Model):
    app_model = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    last_sync_date = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=255, default='', blank=True)
    requires = models.ManyToManyField('self', symmetrical=False, blank=True)
    get_elements_class_path = models.CharField(max_length=255,
        default='django_data_sync.getters.APIJson')
    get_elements_data_json = JSONField(default={}, blank=True,
        load_kwargs={'object_pairs_hook': OrderedDict})
    load_elements_class_path = models.CharField(max_length=255,
        default='django_data_sync.loaders.Base')
    load_elements_data_json = JSONField(default={}, blank=True,
        load_kwargs={'object_pairs_hook': OrderedDict})

    def __init__(self, *args, **kwargs):
        super(SyncAppModel, self).__init__(*args, **kwargs)
        self._get_elements_class = None
        self._load_elements_class = None

    def __str__(self):
        return self.app_model

    def __unicode__(self):
        return u'%s' % self.app_model

    @property
    def get_elements_data(self):
        return self.get_elements_data_json

    @get_elements_data.setter
    def get_elements_data(self, data):
        self.get_elements_data_json = data

    @property
    def load_elements_data(self):
        return self.load_elements_data_json

    @load_elements_data.setter
    def load_elements_data(self, data):
        self.load_elements_data_json = data

    @staticmethod
    def get_class(class_path):
        class_package = '.'.join(class_path.split('.')[:-1])
        class_name = class_path.split('.')[1]
        class_import = __import__(class_package, fromlist=[class_name, ])
        return getattr(class_import, class_name)

    @property
    def get_elements_class(self):
        if self._get_elements_class is None:
            self._get_elements_class = self.get_class(self.get_elements_class_path)
        return self._get_elements_class

    @property
    def load_elements_class(self):
        if self._load_elements_class is None:
            self._load_elements_class = self.get_class(self.load_elements_class_path)
        return self._load_elements_class

    def get_absolute_url(self):
        return reverse('django_data_sync:sync_app_model_detail',
                       kwargs={'pk': self.pk})
