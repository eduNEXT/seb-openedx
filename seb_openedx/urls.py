""" urls.py """

from django.conf.urls import url
from seb_openedx import views


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^seb-info$', views.info_view),
]
