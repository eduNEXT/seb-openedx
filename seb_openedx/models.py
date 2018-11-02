""" Models """
from __future__ import absolute_import, unicode_literals
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField


class ForbiddenCourseAccess(models.Model):
    """ user_id <-> course_id relation to mark forbidden users """
    username = models.CharField(max_length=150)  # from django.contrib.auth.user
    course_id = CourseKeyField(max_length=255)  # from CourseOverview
    access_blocked = models.BooleanField(default=True)  # from CourseOverview
    last_modified_time = models.DateTimeField(auto_now_add=True)
    last_modified_by_username = models.CharField(max_length=150)

    class Meta(object):
        """ Meta """
        unique_together = ('username', 'course_id')
        indexes = [
            models.Index(fields=['username', 'course_id'])
        ]
