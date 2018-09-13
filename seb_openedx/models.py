from django.db import models
from opaque_keys.edx.django.models import CourseKeyField


class ForbiddenCourseAccess(models.Model):
    """ user_id <-> course_id relation to mark forbidden users """
    user_id = models.CharField(max_length=150)  # from django.contri.auth.user
    course_id = CourseKeyField(max_length=255)  # from CourseOverview
