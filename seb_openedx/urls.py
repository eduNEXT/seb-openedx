""" urls.py """

from django.conf.urls import url, include
from seb_openedx import views


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^seb-info$', views.info_view),
    url(r'^dashboard/', include(('seb_openedx.dashboard.urls', 'seb_openedx'), namespace='seb-dashboard')),
    url(r'^api/', include(('seb_openedx.api.urls', 'seb_openedx'), namespace='seb-api')),
]
