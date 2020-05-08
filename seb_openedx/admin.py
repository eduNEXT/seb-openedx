# -*- coding: utf-8 -*-
""" Admin.py """
from django.contrib import admin
from django.db.models import TextField
from seb_openedx.forms import SebCourseConfigurationForm
from seb_openedx.models import (
    ForbiddenCourseAccess,
    SebCourseConfiguration,
)
from seb_openedx.widgets import ListWidget


class SebCourseConfigurationAdmin(admin.ModelAdmin):
    """Admin for the SebCourseConfiguration model."""
    list_display = [
        'course_id',
        'user_banning_enabled',
    ]
    search_fields = ('course_id', )
    formfield_overrides = {
        TextField: {'widget': ListWidget}
    }
    form = SebCourseConfigurationForm


admin.site.register(ForbiddenCourseAccess)
admin.site.register(SebCourseConfiguration, SebCourseConfigurationAdmin)
