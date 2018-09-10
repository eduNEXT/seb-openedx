""" Middleware for seb_openedx """

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error
from seb_openedx.permissions import AlwaysAllowStaff, CheckSEBKeys
from seb_openedx.edxapp_wrapper.get_course_module import get_course_module


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    allow = [AlwaysAllowStaff, CheckSEBKeys]

    # pylint: disable=inconsistent-return-statements
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        course_key = CourseKey.from_string(course_key_string) if course_key_string else None
        if course_key:
            course_module = get_course_module(course_key, depth=0)
            for permission in self.allow:
                if permission().check(request, course_module):
                    return
            return HttpResponseForbidden("Access Forbidden: This course can only be accessed with Safe Exam Browser")
