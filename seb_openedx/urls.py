""" urls.py """

from django.urls import re_path, include
from seb_openedx import views


urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^seb-info$', views.info_view),
    re_path(r'^dashboard/', include('seb_openedx.dashboard.urls', namespace='seb-dashboard')),
    re_path(r'^api/', include('seb_openedx.api.urls', namespace='seb-api')),
]
