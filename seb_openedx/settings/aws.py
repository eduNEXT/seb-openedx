"""
Settings for seb_openedx
"""

from __future__ import absolute_import, unicode_literals


def plugin_settings(settings):
    """
    Defines seb_openedx settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    if not hasattr(settings, 'SEB_KEYS'):
        settings.SEB_KEYS = getattr(settings, 'ENV_TOKENS', {}).get('SEB_KEYS', {})
