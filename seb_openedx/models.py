""" Models """
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField

from seb_openedx.constants import SEPARATOR_CHAR


def get_default_array_value(setting_value):
    """Get default value from settings."""
    if setting_value:
        return SEPARATOR_CHAR.join(setting_value)
    return ''


class ForbiddenCourseAccess(models.Model):
    """ user_id <-> course_id relation to mark forbidden users """
    username = models.CharField(max_length=150)  # from django.contrib.auth.user
    course_id = CourseKeyField(max_length=255)  # from CourseOverview
    access_blocked = models.BooleanField(default=True)  # from CourseOverview
    last_modified_time = models.DateTimeField(auto_now_add=True)
    last_modified_by_username = models.CharField(max_length=150)

    def __unicode__(self):
        """ Nice printing """
        return f"{self.username} at {self.course_id}"

    class Meta:
        """ Meta """
        unique_together = ('username', 'course_id')
        app_label = 'seb_openedx'
        indexes = [
            models.Index(fields=['username', 'course_id'])
        ]


class SebCourseConfiguration(models.Model):
    """Model that stores settings per course for seb browser."""
    course_id = CourseKeyField(max_length=255, unique=True)
    permission_components = models.TextField(
        blank=True,
        default=get_default_array_value(getattr(settings, 'SEB_PERMISSION_COMPONENTS', [])),
    )
    browser_keys = models.TextField(blank=True, default='')
    config_keys = models.TextField(blank=True, default='')
    user_banning_enabled = models.BooleanField(
        default=getattr(settings, 'SEB_USER_BANNING_ENABLED', False),
    )

    class Meta:
        """Meta."""
        app_label = 'seb_openedx'

    def __str__(self):
        """Formats impression of object."""
        return str(self.course_id)

    @classmethod
    def get_as_dict_by_course_id(cls, course_id):
        """Get config by course_id."""
        instance = cls.objects.get(course_id=course_id)
        permission_components = [_f for _f in instance.permission_components.split(SEPARATOR_CHAR) if _f]
        browser_keys = [_f for _f in instance.browser_keys.split(SEPARATOR_CHAR) if _f]
        config_keys = [_f for _f in instance.config_keys.split(SEPARATOR_CHAR) if _f]
        return {
            'PERMISSION_COMPONENTS': permission_components,
            'BROWSER_KEYS': browser_keys,
            'CONFIG_KEYS': config_keys,
            'USER_BANNING_ENABLED': instance.user_banning_enabled,
        }
