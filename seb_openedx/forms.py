# -*- coding: utf-8 -*-
"""
Forms for seb-openedx.
"""
from __future__ import absolute_import

from django import forms
from django.utils.translation import gettext_lazy as _

from seb_openedx.constants import SEB_ARRAY_FIELDS_MODEL, SEPARATOR_CHAR
from seb_openedx.models import SebCourseConfiguration


class SebCourseConfigurationForm(forms.ModelForm):
    """Form model for SebCourseConfiguration."""
    array_fields = SEB_ARRAY_FIELDS_MODEL

    class Meta:
        """Meta."""
        model = SebCourseConfiguration
        fields = [
            'course_id',
            'permission_components',
            'browser_keys',
            'config_keys',
            'user_banning_enabled',
            'blacklist_chapters',
            'whitelist_paths',
        ]
        help_texts = {
            'permission_components': _("""Add a list of permmission components class separated by linebreak e.g:<br><br>
                                       AlwaysAllowStaff <br>
                                       CheckSEBHashBrowserExamKey <br>
                                       CheckSEBHashConfigKey"""),
            'browser_keys': _("""Add a list of browser keys separated by linebreak e.g:<br><br>
                                       cd8827e4555e4eef82........5088a4bd5c9887f32e590 <br>
                                       ddd3f148d87776a571........dea39931ec8ea1b2bca21"""),
            'config_keys': _("""Add a list of config keys separated by linebreak e.g:<br><br>
                                       cd8827e4555e4eef82........5088a4bd5c9887f32e590 <br>
                                       ddd3f148d87776a571........dea39931ec8ea1b2bca21"""),
            'blacklist_chapters': _("""Add a list of chapters (Studio: sections) separated by linebreak e.g:<br><br>
                                       e87b8744ea3949989f8aa113ad428515 <br>
                                       33aa125724414ad090a1842ec244e11e"""),
            'blacklist_sequences': _("""Add a list of sequences (Studio: subsections) separated by linebreak e.g:<br><br>
                                       f80c166b31da4a129f2d23f9fe8bb97b <br>
                                       4fc9a24a783840bd9b50a29fe2ca27e4"""),
            'blacklist_verticals': _("""Add a list of vertical (Studio: units) separated by linebreak e.g:<br><br>
                                       d30d79a1f41445cdb6125de70a88ff7d <br>
                                       43405e86a57143e9953e3d990bece4e4"""),
            'whitelist_paths': _("""Add a list of paths separated by linebreak e.g:<br><br>
                                    about <br>
                                    course-outline <br>
                                    courseware **used for restricting chapters, sequences or verticals<br>
                                    discussion <br>
                                    progress <br>
                                    wiki""")
        }

    def _format_array_field(self, data_field):
        """Adapt array field content from breakline format to 'val1.val2.val3'."""
        result = data_field.split('\r\n')
        result = SEPARATOR_CHAR.join(result)
        return result.strip(SEPARATOR_CHAR)

    def clean(self):
        """Format array fields."""
        for field in self.array_fields:
            self.cleaned_data[field] = self._format_array_field(self.cleaned_data[field])
        return self.cleaned_data
