""" Module that handles CMS and LMS views """

from django.http import HttpResponseForbidden
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from seb_openedx.utils import parse_json_maybe


def cms(request, course_module):
    """ Add "seb_keys":[] if doesn't exist already """
    other_settings = course_module.other_course_settings
    if request.user.is_staff and 'seb_keys' not in other_settings:
        if request.method == 'GET' or 'seb_keys' not in parse_json_maybe(request.body, {}):
            other_settings['seb_keys'] = []
            to_save = {'other_course_settings': other_settings}
            for key, value in to_save.iteritems():
                setattr(course_module, key, value)
            modulestore().update_item(course_module, request.user.id)


# pylint: disable=inconsistent-return-statements
def lms(request, course_module):
    """ Handle lms view """
    other_settings = course_module.other_course_settings
    header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH'
    if 'seb_keys' in other_settings and other_settings['seb_keys']:
        if request.user.is_staff:
            return
        elif header in request.META and request.META[header] in other_settings['seb_keys']:
            return
        return HttpResponseForbidden("Access Forbidden: This course can only be accessed with Safe Exam Browser")
