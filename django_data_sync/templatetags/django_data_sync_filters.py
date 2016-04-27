from collections import OrderedDict

from django import template
from django.contrib.auth.models import Group

from django_data_sync import sync

register = template.Library()


@register.filter
def dk(dictionary, dict_key):
    if not dictionary:
        return None
    element = None
    if dictionary:
        if dict_key in dictionary.keys():
            return dictionary[dict_key]
        if str(dict_key) in dictionary.keys():
            return dictionary[str(dict_key)]
    return element


@register.filter
def is_dict(obj):
    return type(obj) in [dict, OrderedDict]


@register.filter
def ordered_app_model_instances_list(sync_app_model):
    return sync.ordered_app_model_instances(sync_app_model)
