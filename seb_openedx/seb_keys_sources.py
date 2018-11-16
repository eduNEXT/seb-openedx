"""
SEB KEYS FETCHING
Available functions that can be used to fetch Secure Exam Browser keys
"""
from django.utils import six
from django.conf import settings
from seb_openedx.edxapp_wrapper.get_course_module import get_course_module
from seb_openedx.edxapp_wrapper.get_configuration_helpers import get_configuration_helpers


def from_other_course_settings(course_key):
    """
    ENABLE_OTHER_COURSE_SETTINGS must be enabled for this option to work,
    meaning Open edX version >= release-2018-08-07-11.59 (e.g. Hawtorn doesn't work)
    """
    course_module = get_course_module(course_key, depth=0)
    if hasattr(course_module, 'other_course_settings'):
        other_settings = course_module.other_course_settings
        return other_settings.get('SEB_KEYS', None)
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


def from_site_configuration(course_key):
    """
    Get SEB keys from djangoapps.site_configuration
    """
    configuration_helpers = get_configuration_helpers()
    if configuration_helpers.has_override_value('SEB_KEYS'):
        keys_dict = configuration_helpers.get_configuration_value('SEB_KEYS')
        return keys_dict.get(six.text_type(course_key), None)
    return None


def get_ordered_seb_keys_sources():
    """ get key sources as specified on settings, or the default ones """
    # First one has precedence over second, second over third and so forth.
    if hasattr(settings, 'SEB_KEY_SOURCES'):
        return [globals()[source] for source in settings.SEB_KEY_SOURCES]
    return [from_global_settings, from_other_course_settings, from_site_configuration]
