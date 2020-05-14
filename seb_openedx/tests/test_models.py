"""
Test models for seb-openedx.
"""
from django.test import TestCase
from opaque_keys.edx.keys import CourseKey
from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.models import SebCourseConfiguration


class TestSebCourseConfiguration(TestCase):
    """Test SebCourseConfiguration model."""

    def setUp(self):
        """setUp."""
        super(TestSebCourseConfiguration, self).setUp()
        self.seb_course_configuration = SebCourseConfiguration.objects.create(
            course_id=CourseKey.from_string('course-v1:edX+DemoX+Demo_Course'),
            permission_components=SEPARATOR_CHAR.join(['AlwaysAllowStaff', 'CheckSEBHashBrowserExamKeyOrConfigKey']),
            browser_keys=SEPARATOR_CHAR.join(['browser_key1', 'browser_key2']),
            config_keys=SEPARATOR_CHAR.join(['config_key1', 'config_key2']),
            user_banning_enabled=False,
            blacklist_chapters='',
            whitelist_paths=''
        )

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
