""" urls for dashboard """
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from seb_openedx.dashboard.views import TableView

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', staff_member_required(TableView.as_view())),
]
