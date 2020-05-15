"""
Test models for seb-openedx.
"""
from django.test import TestCase
from opaque_keys.edx.keys import CourseKey
from seb_openedx.tests.test_utils import get_seb_configuration_instance


class TestSebCourseConfiguration(TestCase):
    """Test SebCourseConfiguration model."""

    def setUp(self):
        """setUp."""
        super(TestSebCourseConfiguration, self).setUp()
        self.seb_course_configuration = get_seb_configuration_instance()

    def test_get_as_dict_by_course_id(self):
        """Must return a dictionary with a valid format for the class SecureExamBrowserMiddleware."""
        config_as_dict = self.seb_course_configuration.get_as_dict_by_course_id(
            CourseKey.from_string('course-v1:edX+DemoX+Demo_Course')
        )
        expected_dict = {
            'PERMISSION_COMPONENTS': ['AlwaysAllowStaff', 'CheckSEBHashBrowserExamKeyOrConfigKey'],
            'BROWSER_KEYS': ['browser_key1', 'browser_key2'],
            'CONFIG_KEYS': ['config_key1', 'config_key2'],
            'USER_BANNING_ENABLED': False,
            'BLACKLIST_CHAPTERS': [],
            'WHITELIST_PATHS': []
        }
        self.assertIsInstance(config_as_dict, dict)
        self.assertDictEqual(config_as_dict, expected_dict)
