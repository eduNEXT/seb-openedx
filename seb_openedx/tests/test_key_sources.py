# -*- coding: utf-8 -*-
"""Tests for the key sources of the SEB Open edX plugin."""
import mock
from django.test import TestCase
from seb_openedx.seb_keys_sources import from_django_model


class TestKeySource(TestCase):
    """
    Test key source functions.
    """
    def setUp(self):
        """Inital configuration settings."""
        super(TestKeySource, self).setUp()
        self.config_example = {
            'PERMISSION_COMPONENTS': ['AlwaysAllowStaff', 'CheckSEBHashBrowserExamKey', 'CheckSEBHashConfigKey'],
            'BLACKLIST_CHAPTERS': [''],
            'CONFIG_KEYS': [''],
            'BROWSER_KEYS': [''],
            'USER_BANNING_ENABLED': False,
            'WHITELIST_PATHS': ['wiki', 'about']
        }

    def test_from_django_model(self):
        """
        Get a valid configuration
        """
        get_as_dict_by_course_id = 'seb_openedx.models.SebCourseConfiguration.get_as_dict_by_course_id'
        with mock.patch(get_as_dict_by_course_id, return_value=self.config_example):
            self.assertEqual(from_django_model('fake_key'), self.config_example)
