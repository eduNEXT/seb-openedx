""" Middleware for seb_openedx """

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from seb_openedx import handle_views


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    def process_request(self, request):
        """ Force this feature to be on (allows usage of "other_course_settings" dict) """
        settings.FEATURES['ENABLE_OTHER_COURSE_SETTINGS'] = True

    # pylint: disable=inconsistent-return-statements
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        if request.user.is_authenticated():
            is_cms = getattr(settings, 'IS_CMS', False)
            course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
            course_key = CourseKey.from_string(course_key_string) if course_key_string else None
            if course_key:
                course_module = modulestore().get_course(course_key, depth=0)
                if is_cms:
                    return handle_views.cms(request, course_module)
                return handle_views.lms(request, course_module)
