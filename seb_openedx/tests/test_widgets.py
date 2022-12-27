# -*- coding: utf-8 -*-
"""
Test widgets for seb-openedx.
"""
from django.test import TestCase
from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.widgets import ListWidget


class TestListWidget(TestCase):
    """Test the functionality of the ListWidget class."""

    def test_template_values(self):
        """Must be return a list with the values to the template."""
        name = 'text_field_input'
        value = SEPARATOR_CHAR.join(['key1', 'key2', 'key3'])
        list_widget = ListWidget().get_context(name=name, value=value, attrs={})
        self.assertEqual(list_widget['widget']['value'], ['key1', 'key2', 'key3'])
        self.assertEqual(list_widget['widget']['name'], 'text_field_input')
