""" Middleware for seb_openedx """

import sys
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from seb_openedx.permissions import AlwaysAllowStaff, CheckSEBKeysRequestHash


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
            return HttpResponseForbidden("Access Forbidden: This course can only be accessed with Safe Exam Browser")

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares
