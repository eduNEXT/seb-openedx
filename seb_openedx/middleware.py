""" Middleware for seb_openedx """

import sys
import os
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from seb_openedx.permissions import AlwaysAllowStaff, CheckSEBKeysRequestHash
from seb_openedx.edxapp_wrapper.get_edxmako_module import get_edxmako_module


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    allow = [AlwaysAllowStaff, CheckSEBKeysRequestHash]

    # pylint: disable=inconsistent-return-statements
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        course_key = CourseKey.from_string(course_key_string) if course_key_string else None
        if course_key:
            for permission in self.allow:
                if permission().check(request, course_key):
                    return
            return self.render_to_response('seb-403.html', status=403)

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares

    def render_to_response(self, template_name, dictionary=None, namespace='main', request=None, **kwargs):
        """ Custom render_to_response implementation using configurable backend and adding template dir """
        edxmako = get_edxmako_module()
        if os.path.dirname(os.path.abspath(__file__)) + '/templates' not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', 'templates', 'seb_openedx')
        return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)
