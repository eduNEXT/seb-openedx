# -*- coding: utf-8 -*-
""" Configuration as explained on tutorial
github.com/edx/edx-platform/tree/master/openedx/core/djangoapps/plugins"""
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class SebOpenEdxConfig(AppConfig):
    """App configuration"""
    name = 'seb_openedx'
    verbose_name = "Safe Exam Browser"
    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'seb-openedx',
                'regex': r'^seb-openedx/',
                'relative_path': 'urls',
            },
        },
        'settings_config': {
            'lms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'aws': {'relative_path': 'settings.aws'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }
