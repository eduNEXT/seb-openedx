# -*- coding: utf-8 -*-
"""Tests for the key sources of the SEB Open edX plugin."""
import mock
from django.test import TestCase
from opaque_keys.edx.django.models import CourseKey
from seb_openedx.models import SebCourseConfiguration
from seb_openedx.seb_keys_sources import from_django_model, to_django_model
from seb_openedx.tests.test_utils import get_seb_configuration_instance


class TestKeySource(TestCase):
    """
    Test key source functions.
    """
    def setUp(self):
        """Inital configuration settings."""
        super(TestKeySource, self).setUp()
        self.config_example = {
            'PERMISSION_COMPONENTS': ['AlwaysAllowStaff', 'CheckSEBHashBrowserExamKey', 'CheckSEBHashConfigKey'],
            'BLACKLIST_CHAPTERS': [],
            'CONFIG_KEYS': [],
            'BROWSER_KEYS': [],
            'USER_BANNING_ENABLED': False,
            'WHITELIST_PATHS': ['wiki', 'about']
        }
        self.seb_course_configuration = get_seb_configuration_instance()

    def test_success_from_django_model(self):
        """
        Get a valid configuration.
        """
        get_as_dict_by_course_id = 'seb_openedx.models.SebCourseConfiguration.get_as_dict_by_course_id'
        with mock.patch(get_as_dict_by_course_id, return_value=self.config_example):
            self.assertEqual(from_django_model('fake_key'), self.config_example)

    def test_not_found_from_django_model(self):  # pylint: disable=invalid-name
        """
        Should happen when no instance is found for SebCourseConfiguration.
        """
        get_as_dict_by_course_id = 'seb_openedx.models.SebCourseConfiguration.get_as_dict_by_course_id'
        with mock.patch(get_as_dict_by_course_id, side_effect=SebCourseConfiguration.DoesNotExist):
            self.assertEqual(from_django_model('fake_key'), None)

    def test_sucess_create_to_django_model(self):  # pylint: disable=invalid-name
        """
        Must be set a new SebCourseConfiguration instance.
        """
        config = self.config_example
        config['BLACKLIST_CHAPTERS'] = []
        config['CONFIG_KEYS'] = []
        config['BROWSER_KEYS'] = []
        course_key = CourseKey.from_string('course-v1:edX+DemoX+Second_Course')
        return_value = to_django_model(course_key=course_key, config=config)

        self.assertTrue(return_value)
        self.assertEqual(SebCourseConfiguration.objects.count(), 2)

    def test_sucess_update_to_django_model(self):  # pylint: disable=invalid-name
        """
        Must be update a SebCourseConfiguration instance.
        """
        config = {'PERMISSION_COMPONENTS': ['AlwaysAllowStaff']}
        course_key = CourseKey.from_string('course-v1:edX+DemoX+Demo_Course')
        return_value = to_django_model(course_key=course_key, config=config)
        instance = SebCourseConfiguration.objects.get(course_id=course_key)

        self.assertTrue(return_value)
        self.assertEqual(instance.permission_components, 'AlwaysAllowStaff')

    def test_success_delete_to_django_model(self):  # pylint: disable=invalid-name
        """
        Must be delete a SebCourseConfiguration instance.
        """
        config = None
        course_key = CourseKey.from_string('course-v1:edX+DemoX+Demo_Course')
        return_value = to_django_model(course_key=course_key, config=config)

        self.assertTrue(return_value)
        self.assertEqual(SebCourseConfiguration.objects.count(), 0)
