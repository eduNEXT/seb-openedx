"""
SEB KEYS FETCHING
Available functions that can be used to fetch Secure Exam Browser keys
"""
from django.utils import six
from django.conf import settings
from seb_openedx.edxapp_wrapper.get_course_module import get_course_module


def from_other_course_settings(course_key):
    """
    ENABLE_OTHER_COURSE_SETTINGS must be enabled for this option to work,
    meaning Open edX version >= release-2018-08-07-11.59 (e.g. Hawtorn doesn't work)
    """
    course_module = get_course_module(course_key, depth=0)
    if hasattr(course_module, 'other_course_settings'):
        other_settings = course_module.other_course_settings
        return other_settings.get('seb_keys', None)
    return None


def from_global_settings(course_key):
    """
    Retrieve from global settings, for example:
    # lms/env/common.py
    SEB_KEYS = {
        "course-v1:edX+DemoX+Demo_Course": ["FAKE_SEB_KEY"]
    }
    """
    if hasattr(settings, 'SEB_KEYS'):
        return settings.SEB_KEYS.get(six.text_type(course_key), None)
    return None


# First one has precedence over second, second over third and so forth.
ORDERED_SEB_KEYS_SOURCES = [from_global_settings, from_other_course_settings]
