from django import template
import os

register = template.Library()

@register.simple_tag(name='get_system_version')
def get_system_version(*args, **kwargs):
    return os.environ.get('SYSTEM_VERSION') or 'latest'