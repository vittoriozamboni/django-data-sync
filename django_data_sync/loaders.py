import json

import dateutil.parser

from django.core.serializers import deserialize


class LoaderMixin(object):

    def __init__(self, app_model):
        self.app_model = app_model
        self._model_class = None

    @property
    def model_class(self):
        if not self._model_class:
            class_package = '.'.join(self.app_model.app_model.split('.')[:-1])
            class_name = self.app_model.app_model.split('.')[-1]
            class_import = __import__(class_package, fromlist=[class_name, ])
            self._model_class = getattr(class_import, class_name)
        return self._model_class

    def load_element(self, element):
        pass

    def load_elements(self, elements):
        for element in elements:
            self.load_element(element)


class Model(LoaderMixin):

    def load_element(self, element, **kwargs):
        fields = {k: v for k, v in element.iteritems()}

        if kwargs.get('auto_date', True):
            for attr, value in fields.iteritems():
                if attr.startswith('date_') or attr.endswith('_date'):
                    fields[attr] = dateutil.parser.parse(value)

        Model = self.model_class
        instance = Model(**fields)
        instance.save()


class DjangoDeserialize(LoaderMixin):

    def load_elements(self, elements, **kwargs):

        if kwargs.get('transform_elements'):
            serialized_elements = []
            for element in elements:
                serialized_elements.append({
                    'model': self.app_model.app_model.replace('.models', ''),
                    'pk': element['pk'],
                    'fields': {k: v for k, v in element.iteritems()}
                })
            serialized_elements = json.dumps(serialized_elements)
        else:
            serialized_elements = elements
        for instance in deserialize('json', serialized_elements,
                                    ignorenonexistent=kwargs.get('ignorenonexistent', True)):
            instance.save()

