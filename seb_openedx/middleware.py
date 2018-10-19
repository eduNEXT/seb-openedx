""" Middleware for seb_openedx """

import sys
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from seb_openedx.edxapp_wrapper.edxmako_module import render_to_response
from seb_openedx.permissions import get_enabled_permission_classes


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        course_key = CourseKey.from_string(course_key_string) if course_key_string else None
        if course_key:
            active_comps = get_enabled_permission_classes()
            for permission in active_comps:
                if permission().check(request, course_key):
                    return None
            return render_to_response('seb-403.html', status=403)
        return None

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares
