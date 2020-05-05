# -*- coding: utf-8 -*-
"""Handles the /seb-openedx/dashboard/ feature"""

from __future__ import unicode_literals
from opaque_keys.edx.keys import CourseKey
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic import TemplateView
from django.shortcuts import render
from seb_openedx.user_banning import ban_user, unban_user, get_all_banning_data


class TableView(TemplateView):  # pylint: disable=too-many-ancestors
    """ Table view using django_tables2 """
    def get(self, request, *args, **kwargs):
        all_instances = get_all_banning_data()
        return render(request, "seb-manage-users/table.html", {"all_instances": all_instances})

    def post(self, request, *args, **kwargs):
        """ handle POST requests """
        action = request.POST.get("action", False)

        username = request.POST.get("username", None)
        course_id = request.POST.get("course_id", None)
        course_key = CourseKey.from_string(course_id)

        if action == "unban":
            unban_user(username, course_key, request.user.username)

        elif action == "ban":
            banned, _ = ban_user(username, course_key, request.user.username)
            if not banned:
                return HttpResponseBadRequest("Could not ban the user from this page")

        return HttpResponseRedirect(self.request.path_info)
