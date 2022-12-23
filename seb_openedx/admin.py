# -*- coding: utf-8 -*-
""" Admin.py """
from __future__ import absolute_import

from django.contrib import admin
from django.db.models import Q, TextField

from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.forms import SebCourseConfigurationForm
from seb_openedx.models import ForbiddenCourseAccess, SebCourseConfiguration
from seb_openedx.widgets import ListWidget

MAX_CHAR_KEYS = 7
MAX_KEYS = 3
LIST_SEPARATOR = '...'


class SebCourseConfigurationAdmin(admin.ModelAdmin):
    """Admin for the SebCourseConfiguration model."""
    list_display = [
        'course_id',
        'user_banning_enabled',
        'seb_permission_components',
        'seb_browser_keys',
        'seb_config_keys',
        'seb_whitelist_paths',
        'seb_blacklist_chapters',
    ]
    search_fields = ('course_id', )
    formfield_overrides = {
        TextField: {'widget': ListWidget}
    }
    form = SebCourseConfigurationForm

    def get_search_results(self, request, queryset, search_term):
        """Add the filter to search by config_keys and browser_keys."""
        queryset, use_distinct = super(SebCourseConfigurationAdmin, self).get_search_results(
            request,
            queryset,
            search_term
        )
        queryset |= self.model.objects.filter(
            Q(browser_keys__startswith=search_term) | Q(config_keys__startswith=search_term)
        )
        return queryset, use_distinct

    def shows_simplified_list(self, keys_string):
        """Separate the lists for better visualization in the admin."""
        keys = []
        for key in keys_string.split(SEPARATOR_CHAR)[:MAX_KEYS]:
            keys.append(key[:MAX_CHAR_KEYS])
        return LIST_SEPARATOR.join(keys)

    def seb_permission_components(self, obj):
        """Show in list view the permission_components."""
        return self.shows_simplified_list(obj.permission_components)

    def seb_config_keys(self, obj):
        """Show in list view the config_keys."""
        return self.shows_simplified_list(obj.config_keys)

    def seb_browser_keys(self, obj):
        """show in list view the browser_keys"""
        return self.shows_simplified_list(obj.browser_keys)

    def seb_whitelist_paths(self, obj):
        """show in list view the whitelist_paths"""
        return self.shows_simplified_list(obj.whitelist_paths)

    def seb_blacklist_chapters(self, obj):
        """show in list view the blacklist_chapters"""
        return self.shows_simplified_list(obj.blacklist_chapters)


admin.site.register(ForbiddenCourseAccess)
admin.site.register(SebCourseConfiguration, SebCourseConfigurationAdmin)
