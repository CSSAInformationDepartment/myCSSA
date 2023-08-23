import os

from django import template

register = template.Library()


@register.simple_tag(name='get_system_version')
def get_system_version(*args, **kwargs):
    return os.environ.get('SYSTEM_VERSION') or 'latest'
