""" urls for dashboard """
from django.urls import re_path
from django.contrib.admin.views.decorators import staff_member_required
from seb_openedx.dashboard.views import TableView

app_name = 'seb-dashboard'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^$', staff_member_required(TableView.as_view())),
]
