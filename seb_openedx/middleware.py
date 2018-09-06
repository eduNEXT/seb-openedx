""" Middleware for seb_openedx """

from django.utils.deprecation import MiddlewareMixin
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from seb_openedx.lms import lms


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    # pylint: disable=inconsistent-return-statements
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        if request.user.is_authenticated():
            course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
            course_key = CourseKey.from_string(course_key_string) if course_key_string else None
            if course_key:
                course_module = modulestore().get_course(course_key, depth=0)
                return lms().check_access_allowed(request, course_module)
