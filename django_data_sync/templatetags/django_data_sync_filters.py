from collections import OrderedDict

from django import template
from django.contrib.auth.models import Group

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
