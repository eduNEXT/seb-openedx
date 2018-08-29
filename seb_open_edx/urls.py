""" urls.py """

from django.conf.urls import url
from seb_open_edx import views


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^seb-open-edx$', views.info_view),
]
