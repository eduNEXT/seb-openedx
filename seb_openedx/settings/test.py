"""
Settings for seb_openedx
"""

from __future__ import absolute_import, unicode_literals

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import


class SettingsClass(object):
    """ dummy settings class """
    pass


DEBUG = True
SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)
SEB_COURSEWARE_MODULE = 'seb_openedx.tests.test_utils'
SEB_COURSEWARE_INDEX_VIEW = 'seb_openedx.tests.test_utils'


ROOT_URLCONF = 'seb_openedx.urls'
ALLOWED_HOSTS = ['*']

# This key needs to be defined so that the check_apps_ready passes and the
# AppRegistry is loaded
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
