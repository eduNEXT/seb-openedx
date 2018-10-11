""" Backend abstraction """
import os
import edxmako  # pylint: disable=import-error


def render_to_response(self, template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """ Custom render_to_response implementation using configurable backend and adding template dir """
    if os.path.dirname(os.path.abspath(__file__)) + '/templates' not in edxmako.LOOKUP['main'].directories:
        edxmako.paths.add_lookup('main', 'templates', 'seb_openedx')
    return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)
