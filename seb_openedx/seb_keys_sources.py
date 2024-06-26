"""
SEB KEYS FETCHING
Available functions that can be used to fetch Secure Exam Browser keys
"""
from __future__ import absolute_import

import logging

from django.conf import settings
from django.db.utils import ProgrammingError

from seb_openedx.constants import (SEB_ARRAY_FIELDS_MODEL,
                                   SEB_NOT_TABLES_FOUND, SEPARATOR_CHAR)
from seb_openedx.edxapp_wrapper.get_configuration_helpers import \
    get_configuration_helpers
from seb_openedx.edxapp_wrapper.get_course_module import (
    get_course_module, modulestore_update_item)
from seb_openedx.models import SebCourseConfiguration

LOG = logging.getLogger(__name__)


def from_django_model(course_key):
    """Get SEB settings from model SebCourseConfiguration."""
    try:
        model_settings = SebCourseConfiguration.get_as_dict_by_course_id(course_key)
    except SebCourseConfiguration.DoesNotExist:
        model_settings = None
    except ProgrammingError:
        model_settings = None
        LOG.warning(SEB_NOT_TABLES_FOUND)
    return model_settings


def from_other_course_settings(course_key):
    """
    ENABLE_OTHER_COURSE_SETTINGS must be enabled for this option to work,
    meaning Open edX version >= release-2018-08-07-11.59 (e.g. Hawtorn doesn't work)
    """
    if not settings.FEATURES.get('ENABLE_OTHER_COURSE_SETTINGS', False):
        return None

    course_module = get_course_module(course_key, depth=0)
    if hasattr(course_module, 'other_course_settings'):
        other_settings = course_module.other_course_settings
        other_settings = other_settings.get('SAFE_EXAM_BROWSER', {})
        if str(course_key) in other_settings:
            return other_settings.get(str(course_key), None)
        if other_settings:
            return other_settings
    return None


def to_other_course_settings(course_key, config, **kwargs):
    """
    Set SEB keys on the studio compatible OTHER_COURSE_SETTINGS_DICT.
    Replaces existing configuration
    """
    if not settings.FEATURES.get('ENABLE_OTHER_COURSE_SETTINGS', False):
        return False

    user_id = kwargs.get('user_id', None)
    if not user_id:
        return False

    course_module = get_course_module(course_key, depth=0)

    if not hasattr(course_module.other_course_settings, 'SAFE_EXAM_BROWSER'):
        course_module.other_course_settings['SAFE_EXAM_BROWSER'] = {}

    course_module.other_course_settings['SAFE_EXAM_BROWSER'] = config

    try:
        modulestore_update_item(course_key, course_module, user_id)
    except Exception as error:  # pylint: disable=broad-except
        LOG.error("Could not store SEB configuration for %s on other_settings, due to %s", course_key, error)
        return False

    return True


def from_global_settings(course_key):
    """
    Retrieve from global settings, for example:
    # lms/env/common.py
    SAFE_EXAM_BROWSER = {
        "course-v1:edX+DemoX+Demo_Course": ["FAKE_SEB_KEY"]
    }
    """
    if hasattr(settings, 'SAFE_EXAM_BROWSER'):
        return settings.SAFE_EXAM_BROWSER.get(str(course_key), None)
    return None


def from_global_settings_default_keys(*args):
    """
    Retrieve from global settings using the default key, ignores course_key, for example:
    # lms/env/common.py
    SAFE_EXAM_BROWSER = {
        "default": ["FAKE_SEB_KEY"]
    }
    """
    if hasattr(settings, 'SAFE_EXAM_BROWSER'):
        return settings.SAFE_EXAM_BROWSER.get('default', None)
    return None


def from_site_configuration_default_keys(*args):
    """
    Get SEB keys from djangoapps.site_configuration ignoring course_key and using the default
    """
    configuration_helpers = get_configuration_helpers()
    if configuration_helpers.has_override_value('SAFE_EXAM_BROWSER'):
        keys_dict = configuration_helpers.get_configuration_value('SAFE_EXAM_BROWSER')
        return keys_dict.get('default', None)
    return None


def from_site_configuration(course_key):
    """
    Get SEB keys from djangoapps.site_configuration
    """
    configuration_helpers = get_configuration_helpers()
    if configuration_helpers.has_override_value('SAFE_EXAM_BROWSER'):
        keys_dict = configuration_helpers.get_configuration_value('SAFE_EXAM_BROWSER')
        return keys_dict.get(str(course_key), None)
    return None


def to_django_model(course_key, config, **kwargs):
    """
    Set SEB keys on SebCourseConfiguration
    Update existing configuration
    Delete if config is None.
    """
    if not config:
        try:
            SebCourseConfiguration.objects.get(course_id=course_key).delete()
        except SebCourseConfiguration.DoesNotExist:
            LOG.info('seb_plugin: there is no configuration for this course %s', str(course_key))
            return False
        except ProgrammingError:
            LOG.warning(SEB_NOT_TABLES_FOUND)
            return False
        return True
    config = {key.lower(): value for key, value in config.items()}  # keys to lowercase
    for key in SEB_ARRAY_FIELDS_MODEL:
        if key in config:
            config[key] = SEPARATOR_CHAR.join(config[key])
    try:
        SebCourseConfiguration.objects.update_or_create(
            course_id=course_key,
            defaults=config
        )
    except ProgrammingError:
        LOG.warning(SEB_NOT_TABLES_FOUND)
        return False
    return True


def to_site_configuration(course_key, config, **kwargs):
    """
    Set SEB keys on djangoapps.site_configuration.
    Replaces existing configuration
    """
    course_id = str(course_key)

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
    return [from_global_settings, from_other_course_settings, from_django_model, from_site_configuration]


def get_config_by_course(course_key):
    """ get seb config for course """
    for source_function in get_ordered_seb_keys_sources():
        _config = source_function(course_key)
        if isinstance(_config, dict):
            return _config
    return {}


def get_ordered_seb_keys_dest():
    """ Get key storage locations as specified on settings, or the default ones """
    if hasattr(settings, 'SEB_KEY_DESTINATIONS'):
        return [globals()[source] for source in settings.SEB_KEY_DESTINATIONS]
    return [to_django_model, to_other_course_settings, to_site_configuration]


def save_course_config(course_key, config, **kwargs):
    """
    Sets the configuration to the first available destination
    """
    for destination_function in get_ordered_seb_keys_dest():
        if destination_function(course_key, config, **kwargs):
            return True
    return False
