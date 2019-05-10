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
        return other_settings.get('SAFE_EXAM_BROWSER', None)
    return None


def from_global_settings(course_key):
    """
    Retrieve from global settings, for example:
    # lms/env/common.py
    SAFE_EXAM_BROWSER = {
        "course-v1:edX+DemoX+Demo_Course": ["FAKE_SEB_KEY"]
    }
    """
    if hasattr(settings, 'SAFE_EXAM_BROWSER'):
        return settings.SAFE_EXAM_BROWSER.get(six.text_type(course_key), None)
    return None


def from_site_configuration(course_key):
    """
    Get SEB keys from djangoapps.site_configuration
    """
    configuration_helpers = get_configuration_helpers()
    if configuration_helpers.has_override_value('SAFE_EXAM_BROWSER'):
        keys_dict = configuration_helpers.get_configuration_value('SAFE_EXAM_BROWSER')
        return keys_dict.get(six.text_type(course_key), None)
    return None


def to_site_configuration(course_key, config):
    """
    Set SEB keys on djangoapps.site_configuration.
    Replaces existing configuration
    """
    course_id = six.text_type(course_key)

    site_configuration = get_configuration_helpers().get_current_site_configuration()

    if not site_configuration:
        return False

    if 'SAFE_EXAM_BROWSER' not in site_configuration.values:
        site_configuration.values['SAFE_EXAM_BROWSER'] = {}

    site_configuration.values['SAFE_EXAM_BROWSER'][course_id] = config
    site_configuration.save()
    return True


def get_ordered_seb_keys_sources():
    """ get key sources as specified on settings, or the default ones """
    # First one has precedence over second, second over third and so forth.
    if hasattr(settings, 'SEB_KEY_SOURCES'):
        return [globals()[source] for source in settings.SEB_KEY_SOURCES]
    return [from_global_settings, from_other_course_settings, from_site_configuration]


def get_config_by_course(course_key):
    """ get seb config for course """
    for source_function in get_ordered_seb_keys_sources():
        _config = source_function(course_key)
        if isinstance(_config, dict):
            return _config
    return {}


def get_ordered_seb_keys_destinations():
    """ Get key storage locations as specified on settings, or the default ones """
    if hasattr(settings, 'SEB_KEY_DESTINATIONS'):
        return [globals()[source] for source in settings.SEB_KEY_DESTINATIONS]
    return [to_site_configuration]


def save_course_config(course_key, config):
    """
    Sets the configuration to the
    """
    for destination_function in get_ordered_seb_keys_destinations():
        if destination_function(course_key, config):
            return True
    return False
