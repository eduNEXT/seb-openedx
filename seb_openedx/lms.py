""" Module that handles CMS and LMS views """

from django.http import HttpResponseForbidden
from options_as_decorators import always_allow_staff


class lms(object):

    # pylint: disable=inconsistent-return-statements
    @always_allow_staff
    def check_access_allowed(self, request, course_module):
        """ Handle lms view """
        other_settings = course_module.other_course_settings
        header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH'
        if 'seb_keys' in other_settings and other_settings['seb_keys']:
            if header in request.META and request.META[header] in other_settings['seb_keys']:
                return
            return HttpResponseForbidden("Access Forbidden: This course can only be accessed with Safe Exam Browser")
