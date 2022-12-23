# -*- coding: utf-8 -*-
"""
Widgets for seb-openedx forms.
"""
from __future__ import absolute_import

from django.forms.widgets import Widget

from seb_openedx.constants import SEPARATOR_CHAR


class ListWidget(Widget):
    """
    Converts a string array to a list separated by line breaks,
    for better visualization in the forms.
    """
    template_name = 'widgets/list_widget.html'

    def get_context(self, name, value, attrs):
        """
        Format the values ​​before sending them to the template.
        """
        try:
            value = value.split(SEPARATOR_CHAR)
        except AttributeError:
            value = ''
        return {
            'widget': {
                'name': name,
                'value': value,
            }
        }
