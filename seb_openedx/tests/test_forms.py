# -*- coding: utf-8 -*-
"""
Test forms for seb-openedx.
"""
from django.test import TestCase
from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.forms import SebCourseConfigurationForm


class TestSebCourseConfigurationForm(TestCase):
    """Test the form SebCourseConfigurationForm."""
    def setUp(self):
        """setUp."""
        super(TestSebCourseConfigurationForm, self).setUp()
        self.form_data = {
            'course_id': 'course-v1:edX+DemoX+Demo_Course',
            'permission_components': 'key1\r\nkey2\r\nkey3'
        }

    def test_valid_form(self):
        """Must be a valid form."""
        form_data = {'course_id': 'course-v1:edX+DemoX+Demo_Course'}
        form = SebCourseConfigurationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_form(self):
        """Must be correctly format the form before saving the record."""
        form = SebCourseConfigurationForm(data=self.form_data)
        expected_cleaned_field = SEPARATOR_CHAR.join(['key1', 'key2', 'key3'])
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean()['permission_components'], expected_cleaned_field)
