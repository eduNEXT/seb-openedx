"""
Forms for seb-openedx.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.models import SebCourseConfiguration


class SebCourseConfigurationForm(forms.ModelForm):
    """Form model for SebCourseConfiguration."""
    array_fields = [
        'permission_components',
        'browser_keys',
        'config_keys',
        'blacklist_chapters',
        'whitelist_paths',
    ]

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
            'permission_components': _("""Add a list of permmission components class ​​separated by linebreak e.g:<br><br>
                                       AlwaysAllowStaff <br>
                                       CheckSEBHashBrowserExamKey <br>
                                       CheckSEBHashConfigKey"""),
            'browser_keys': _("""Add a list of browser keys ​​separated by linebreak e.g:<br><br>
                                       cd8827e4555e4eef82........5088a4bd5c9887f32e590 <br>
                                       ddd3f148d87776a571........dea39931ec8ea1b2bca21"""),
            'config_keys': _("""Add a list of config keys ​​separated by linebreak e.g:<br><br>
                                       cd8827e4555e4eef82........5088a4bd5c9887f32e590 <br>
                                       ddd3f148d87776a571........dea39931ec8ea1b2bca21"""),
            'blacklist_chapters': _("""Add a list of chapters ​​separated by linebreak e.g:<br><br>
                                       e87b8744ea3949989f8aa113ad428515 <br>
                                       33aa125724414ad090a1842ec244e11e"""),
            'whitelist_paths': _("""Add a list of paths ​​separated by linebreak e.g:<br><br>
                                    about <br>
                                    course-outline <br>
                                    courseware <br>
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
