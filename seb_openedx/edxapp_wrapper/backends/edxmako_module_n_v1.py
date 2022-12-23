""" Backend abstraction """
import os
from common.djangoapps import edxmako  # pylint: disable=import-error
if os.path.dirname(os.path.abspath(__file__)) + '/templates' not in edxmako.LOOKUP['main'].directories:
    edxmako.paths.add_lookup('main', 'templates', 'seb_openedx')


def render_to_response(template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """ Custom render_to_response implementation using configurable backend and adding template dir """
    return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)


def render_to_string(template_name, dictionary, namespace='main', request=None):
    """ Custom render_to_string implementation using configurable backend and adding template dir """
    return edxmako.shortcuts.render_to_string(template_name, dictionary, namespace, request)
