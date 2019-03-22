# -*- coding: utf-8 -*-
""" Admin.py """
from django.contrib import admin

from seb_openedx.models import ForbiddenCourseAccess

admin.site.register(ForbiddenCourseAccess)
