from django import forms

from django_helper_forms.forms import DictionaryFieldsForm

import models


class SyncAppModelForm(forms.ModelForm, DictionaryFieldsForm):

    class Meta:
        model = models.SyncAppModel
        exclude = ('last_sync_date', 'last_sync_status')

    def __init__(self, *args, **kwargs):
        super(SyncAppModelForm, self).__init__(*args, **kwargs)
        self.dictionary_fields = ['get_elements_data_json', 'load_elements_data_json']
        self.dictionary_fields_properties = {
            'get_elements_data_json': {'key_label': 'Property', 'value_label': 'Value'},
            'load_elements_data_json': {'key_label': 'Property', 'value_label': 'Value'},
        }
        self.format_dictionary_fields()
