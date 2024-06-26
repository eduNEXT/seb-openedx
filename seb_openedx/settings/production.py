"""
Settings for seb_openedx
"""

from __future__ import absolute_import, unicode_literals


def plugin_settings(settings):
    """
    Defines seb_openedx settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.SAFE_EXAM_BROWSER = getattr(settings, 'ENV_TOKENS', {}).get('SAFE_EXAM_BROWSER', {})

    settings.SEB_COURSE_MODULE = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_COURSE_MODULE',
        settings.SEB_COURSE_MODULE
    )
    settings.SEB_UPDATE_MODULESTORE = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_UPDATE_MODULESTORE',
        settings.SEB_UPDATE_MODULESTORE
    )
    settings.SEB_COURSEWARE_MODULE = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_COURSEWARE_MODULE',
        settings.SEB_COURSEWARE_MODULE
    )
    settings.SEB_COURSEWARE_INDEX_VIEW = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_COURSEWARE_INDEX_VIEW',
        settings.SEB_COURSEWARE_INDEX_VIEW
    )
    settings.SEB_GET_CHAPTER_FROM_LOCATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_GET_CHAPTER_FROM_LOCATION',
        settings.SEB_GET_CHAPTER_FROM_LOCATION
    )
    settings.SEB_CONFIGURATION_HELPERS = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_CONFIGURATION_HELPERS',
        settings.SEB_CONFIGURATION_HELPERS
    )
    settings.SEB_EDXMAKO_MODULE = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_EDXMAKO_MODULE',
        settings.SEB_EDXMAKO_MODULE
    )
    settings.SEB_PERMISSION_COMPONENTS = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_PERMISSION_COMPONENTS',
        settings.SEB_PERMISSION_COMPONENTS
    )
    settings.SEB_KEY_SOURCES = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_KEY_SOURCES',
        settings.SEB_KEY_SOURCES
    )
    settings.SEB_KEY_DESTINATIONS = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_KEY_DESTINATIONS',
        settings.SEB_KEY_DESTINATIONS
    )
    settings.SEB_USER_BANNING_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_USER_BANNING_BACKEND',
        settings.SEB_USER_BANNING_BACKEND
    )
    settings.SEB_USER_BANNING_ENABLED = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_USER_BANNING_ENABLED',
        settings.SEB_USER_BANNING_ENABLED
    )
    settings.SEB_USE_ALL_SOURCES = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_USE_ALL_SOURCES',
        settings.SEB_USE_ALL_SOURCES
    )
    settings.SEB_ALLOW_MFE_ACCESS = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_ALLOW_MFE_ACCESS',
        settings.SEB_ALLOW_MFE_ACCESS
    )
    settings.SEB_INDIVIDUAL_COURSE_ACTIVATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'SEB_INDIVIDUAL_COURSE_ACTIVATION',
        settings.SEB_INDIVIDUAL_COURSE_ACTIVATION
    )
